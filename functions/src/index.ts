// import { logger } from "firebase-functions";
import * as functions from "firebase-functions";
import * as admin from "firebase-admin";

// The Firebase Admin SDK to access Firestore.
import { initializeApp } from "firebase-admin/app";
import { z } from "zod";
import { ChatOpenAI } from "langchain/chat_models/openai";
import { PromptTemplate } from "langchain/prompts";
import { loadSummarizationChain } from "langchain/chains";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { StructuredOutputParser } from "langchain/output_parsers";
import { ChainValues } from "langchain/dist/schema";

const TOPIC_NAME = "transcription-jobs";

initializeApp();

exports.onmemocreate = functions
  .region("asia-east2")
  .firestore.document("memos/{memoId}")
  .onCreate(async (snap, context) => {
    const { memoId } = context.params;

    const snapshot = snap.data();
    if (!snapshot) {
      console.log("No data associated with the event");
      return;
    }

    try {
      console.log("triggering pubsub");
      const messageId = await admin.messaging().sendToTopic(TOPIC_NAME, {
        data: {
          memoId,
        },
      });
      console.log(`Message ${messageId} published.`);
    } catch (e) {
      console.error("Error in cloud run ", e);
    }
  });

exports.onmemoupdate = functions
  .region("asia-east2")
  .firestore.document("memos/{memoId}")
  .onUpdate(async (change) => {
    const newValue = change.after.data();
    const prevValue = change.before.data();

    if (!newValue) {
      console.log("No data associated with the event | Memo deleted");
      return;
    }

    if (prevValue?.transcript) {
      console.log("Transcript already generated");
      return;
    }

    const { transcript } = newValue;

    const parser = StructuredOutputParser.fromZodSchema(
      z.object({
        summary: z.string().describe("summary of the typescript"),
        tags: z
          .array(z.string())
          .describe(
            "list of entities in the transcript, entities include at most 5 objects of the most interest in the transcript. Entities are most usually nouns."
          ),
      })
    );

    const formatInstructions = parser.getFormatInstructions();

    const model = new ChatOpenAI({
      temperature: 0.9,
      modelName: "gpt-3.5-turbo",
    });

    const textSplitter = new RecursiveCharacterTextSplitter({
      separators: ["\n\n", "\n"],
      chunkSize: 10000,
      chunkOverlap: 500,
    });
    const docs = await textSplitter.createDocuments([transcript]);

    const mapPromptTemplate = new PromptTemplate({
      template: `
    Summarize the given transcript section based on the given format instructions.
    {formatInstructions}
    "{text}"
    `,
      inputVariables: ["text"],
      partialVariables: { formatInstructions: formatInstructions },
    });

    const combinePromptTemplate = new PromptTemplate({
      template: `
    Summarize the given transcript summaries based on the given format instructions. Generate one summary for all the given summaries and combine all the given tags.
    {formatInstructions}
    "{text}"
    `,
      inputVariables: ["text"],
      partialVariables: { formatInstructions: formatInstructions },
    });

    const chain = loadSummarizationChain(model, {
      type: "map_reduce",
      combineMapPrompt: mapPromptTemplate,
      combinePrompt: combinePromptTemplate,
    });

    const result: ChainValues = await chain.call({
      input_documents: docs,
    });

    console.log({ result });

    const parsed = await parser.parse(result.text);

    console.log({ parsed });

    await change.after.ref.update({
      summary: parsed.summary,
      tags: parsed.tags,
    });
  });

// exports["on-memo-update"] = onDocumentUpdated(
//   "memos/{memoId}",
//   async (
//     event: FirestoreEvent<
//       Change<QueryDocumentSnapshot> | undefined,
//       { memoId: string }
//     >
//   ) => {
//     const newValue = event.data?.after.data();
//     const prevValue = event.data?.before.data();
//   }
// );
