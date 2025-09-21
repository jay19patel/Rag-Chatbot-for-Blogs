import dotenv from "dotenv";
import { MistralAI } from "@langchain/mistralai";
import express from "express";
import { BlogsSchema } from "./schema.js";
dotenv.config();

const app = express();
const port = 3000;

// RAG
const llm = new MistralAI({
  model: "codestral-latest",
  temperature: 0,
  maxTokens: undefined,
  maxRetries: 2,
  // other params...
});


const responseFormatterTool = tool(async () => {}, {
  name: "BlogsSchemaFormatter",
  schema: BlogsSchema,
});


const modelWithTools = model.bindTools([responseFormatterTool]);





// Middleware to parse JSON
app.use(express.json());

// Chat endpoint
app.get("/chat", async (req, res) => {
  try {
    const userMessage = req.query.message;
    const completion = await modelWithTools.invoke(userMessage);
    res.json({ completion });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Something went wrong!" });
  }
});

// Start server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
