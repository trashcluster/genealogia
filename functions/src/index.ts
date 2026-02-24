import * as functions from "firebase-functions";
import * as admin from "firebase-admin";
import { auth } from "firebase-admin";
import { Firestore } from "@google-cloud/firestore";
import { Storage } from "@google-cloud/storage";

// Initialize Firebase Admin
admin.initializeApp();
const db: Firestore = admin.firestore();
const storage: Storage = admin.storage();

// Export instances for use in other modules
export { db, storage, auth };

// Import all function modules
export { authFunctions } from "./auth";
export { individualFunctions } from "./individuals";
export { familyFunctions } from "./families";
export { eventFunctions } from "./events";
export { mediaFunctions } from "./media";
export { ingestionFunctions } from "./ingestion";
export { knowledgeFunctions } from "./knowledge";
export { faceRecognitionFunctions } from "./faceRecognition";
export { telegramFunctions } from "./telegram";

// Health check function
export const healthCheck = functions.https.onRequest(async (req, res) => {
  res.status(200).json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    version: "1.0.0",
    services: {
      firestore: "connected",
      storage: "connected",
      auth: "connected"
    }
  });
});

// Example of a scheduled function for maintenance
export const scheduledMaintenance = functions.pubsub
  .schedule("0 2 * * *") // Daily at 2 AM
  .onRun(async (context) => {
    console.log("Running scheduled maintenance tasks");
    
    // Clean up temporary files older than 24 hours
    const tempBucket = storage.bucket("your-app.appspot.com");
    const tempFiles = await tempBucket.getFiles({
      prefix: "temp/"
    });
    
    const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    
    for (const file of tempFiles[0]) {
      const metadata = await file.getMetadata();
      const created = new Date(metadata[0].timeCreated as string);
      
      if (created < twentyFourHoursAgo) {
        await file.delete();
        console.log(`Deleted temporary file: ${file.name}`);
      }
    }
    
    return null;
  });
