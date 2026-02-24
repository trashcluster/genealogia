import * as functions from "firebase-functions";
import * as admin from "firebase-admin";
import { db, storage } from "./index";
import OpenAI from "openai";
import Anthropic from "@anthropic-ai/sdk";
import axios from "axios";

// AI Provider interfaces
interface AIProvider {
  name: string;
  processText(text: string, context?: any): Promise<any>;
  processVoice(audioBuffer: Buffer): Promise<any>;
  processDocument(fileBuffer: Buffer, mimeType: string): Promise<any>;
}

class OpenAIProvider implements AIProvider {
  name = "openai";
  private client: OpenAI;

  constructor(apiKey: string) {
    this.client = new OpenAI({ apiKey });
  }

  async processText(text: string, context?: any): Promise<any> {
    try {
      const response = await this.client.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: `You are a genealogy assistant. Extract structured genealogical data from the provided text. 
            Return a JSON object with individuals, families, events, and relationships.`
          },
          {
            role: "user",
            content: text
          }
        ],
        temperature: 0.3
      });

      return JSON.parse(response.choices[0].message.content || "{}");
    } catch (error) {
      console.error("OpenAI text processing error:", error);
      throw error;
    }
  }

  async processVoice(audioBuffer: Buffer): Promise<any> {
    try {
      const transcription = await this.client.audio.transcriptions.create({
        file: new File([audioBuffer], "audio.wav", { type: "audio/wav" }),
        model: "whisper-1"
      });

      return this.processText(transcription.text);
    } catch (error) {
      console.error("OpenAI voice processing error:", error);
      throw error;
    }
  }

  async processDocument(fileBuffer: Buffer, mimeType: string): Promise<any> {
    // For documents, we'd need OCR or PDF parsing
    // This is a simplified version
    throw new Error("Document processing not implemented for OpenAI");
  }
}

class ClaudeProvider implements AIProvider {
  name = "claude";
  private client: Anthropic;

  constructor(apiKey: string) {
    this.client = new Anthropic({ apiKey });
  }

  async processText(text: string, context?: any): Promise<any> {
    try {
      const response = await this.client.messages.create({
        model: "claude-3-sonnet-20240229",
        max_tokens: 4000,
        messages: [
          {
            role: "user",
            content: `Extract structured genealogical data from this text: ${text}`
          }
        ]
      });

      return JSON.parse(response.content[0].type === "text" ? response.content[0].text : "{}");
    } catch (error) {
      console.error("Claude text processing error:", error);
      throw error;
    }
  }

  async processVoice(audioBuffer: Buffer): Promise<any> {
    // Claude doesn't support audio directly, would need to use a speech-to-text service first
    throw new Error("Voice processing not implemented for Claude");
  }

  async processDocument(fileBuffer: Buffer, mimeType: string): Promise<any> {
    throw new Error("Document processing not implemented for Claude");
  }
}

class OllamaProvider implements AIProvider {
  name = "ollama";
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async processText(text: string, context?: any): Promise<any> {
    try {
      const response = await axios.post(`${this.baseUrl}/api/generate`, {
        model: "llama2",
        prompt: `Extract structured genealogical data from this text: ${text}`,
        stream: false
      });

      return JSON.parse(response.data.response);
    } catch (error) {
      console.error("Ollama text processing error:", error);
      throw error;
    }
  }

  async processVoice(audioBuffer: Buffer): Promise<any> {
    throw new Error("Voice processing not implemented for Ollama");
  }

  async processDocument(fileBuffer: Buffer, mimeType: string): Promise<any> {
    throw new Error("Document processing not implemented for Ollama");
  }
}

// Ingestion service
class IngestionService {
  private providers: AIProvider[] = [];
  private preferredProvider: string = "openai";

  constructor() {
    this.initializeProviders();
  }

  private async initializeProviders() {
    // Initialize providers based on environment variables
    if (process.env.OPENAI_API_KEY) {
      this.providers.push(new OpenAIProvider(process.env.OPENAI_API_KEY));
    }
    
    if (process.env.CLAUDE_API_KEY) {
      this.providers.push(new ClaudeProvider(process.env.CLAUDE_API_KEY));
    }
    
    if (process.env.OLLAMA_URL) {
      this.providers.push(new OllamaProvider(process.env.OLLAMA_URL));
    }
  }

  async processText(text: string, userId: string): Promise<any> {
    const provider = this.getProvider();
    const result = await provider.processText(text);
    
    // Save ingestion log
    await this.saveIngestionLog(userId, "text", text, result);
    
    return result;
  }

  async processVoice(audioBuffer: Buffer, userId: string): Promise<any> {
    const provider = this.getProvider();
    const result = await provider.processVoice(audioBuffer);
    
    // Save ingestion log
    await this.saveIngestionLog(userId, "voice", "audio file", result);
    
    return result;
  }

  async processDocument(fileBuffer: Buffer, mimeType: string, userId: string): Promise<any> {
    const provider = this.getProvider();
    const result = await provider.processDocument(fileBuffer, mimeType);
    
    // Save ingestion log
    await this.saveIngestionLog(userId, "document", mimeType, result);
    
    return result;
  }

  private getProvider(): AIProvider {
    const provider = this.providers.find(p => p.name === this.preferredProvider);
    if (!provider) {
      throw new Error(`Preferred provider ${this.preferredProvider} not available`);
    }
    return provider;
  }

  private async saveIngestionLog(userId: string, type: string, input: any, result: any): Promise<void> {
    const logEntry = {
      userId,
      type,
      input: typeof input === "string" ? input : "binary_data",
      result,
      status: "completed",
      createdAt: admin.firestore.FieldValue.serverTimestamp()
    };

    await db
      .collection("users")
      .doc(userId)
      .collection("ingestion")
      .add(logEntry);
  }
}

// Firebase Cloud Functions
const ingestionService = new IngestionService();

export const processTextIngestion = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }

    const userId = context.auth.uid;
    const { text } = data;

    if (!text || typeof text !== "string") {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "Text is required and must be a string"
      );
    }

    const result = await ingestionService.processText(text, userId);

    return {
      success: true,
      data: result,
      message: "Text processed successfully"
    };
  } catch (error) {
    console.error("Text ingestion error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to process text",
      (error as Error).message
    );
  }
});

export const processVoiceIngestion = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }

    const userId = context.auth.uid;
    const { audioData } = data;

    if (!audioData) {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "Audio data is required"
      );
    }

    const audioBuffer = Buffer.from(audioData, "base64");
    const result = await ingestionService.processVoice(audioBuffer, userId);

    return {
      success: true,
      data: result,
      message: "Voice processed successfully"
    };
  } catch (error) {
    console.error("Voice ingestion error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to process voice",
      (error as Error).message
    );
  }
});

export const processDocumentIngestion = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }

    const userId = context.auth.uid;
    const { fileData, mimeType } = data;

    if (!fileData || !mimeType) {
      throw new functions.https.HttpsError(
        "invalid-argument",
        "File data and MIME type are required"
      );
    }

    const fileBuffer = Buffer.from(fileData, "base64");
    const result = await ingestionService.processDocument(fileBuffer, mimeType, userId);

    return {
      success: true,
      data: result,
      message: "Document processed successfully"
    };
  } catch (error) {
    console.error("Document ingestion error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to process document",
      (error as Error).message
    );
  }
});

export const getIngestionHistory = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }

    const userId = context.auth.uid;
    const { limit = 20, offset = 0 } = data;

    const snapshot = await db
      .collection("users")
      .doc(userId)
      .collection("ingestion")
      .orderBy("createdAt", "desc")
      .limit(limit)
      .offset(offset)
      .get();

    const history = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));

    return {
      success: true,
      history,
      hasMore: history.length === limit
    };
  } catch (error) {
    console.error("Get ingestion history error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to get ingestion history",
      (error as Error).message
    );
  }
});

export const ingestionFunctions = {
  processTextIngestion,
  processVoiceIngestion,
  processDocumentIngestion,
  getIngestionHistory
};
