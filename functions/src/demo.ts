// import { logger } from "firebase-functions";
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

import serviceAccount from "./creds.json";

process.env.OPENAI_API_KEY = "xxxxxxxxxx";

initializeApp({
  credential: admin.credential.cert(serviceAccount as any),
});

const main = async (key: string) => {
  const doc = (await admin.firestore().doc(`memos/${key}`).get()).data();

  if (!doc) {
    console.log("No data associated with the event");
    return;
  }

  const { transcript } = doc;
  const transcriptText = transcript.segments.reduce(
    (acc: string, segment: { text: string }) => acc + segment.text + " ",
    ""
  );
  const parser = StructuredOutputParser.fromZodSchema(
    z.object({
      summary: z.string().describe("summary of the typescript"),
      tags: z
        .array(z.string())
        .describe(
          "list of entities in the transcript, entities include objects of interest in the transcript. Entities are most usually nouns."
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
  const docs = await textSplitter.createDocuments([transcriptText]);

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

  // await change.after.ref.update({
  //   summary: parsed.summary,
  //   tags: parsed.tags,
  // });
};

main("5HYf1QYDqe7QOWKICeY9");
