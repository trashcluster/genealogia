import * as functions from "firebase-functions";
import { auth } from "firebase-admin";
import { db } from "./index";

// User registration
export const register = functions.https.onCall(async (data, context) => {
  try {
    const { email, password, username } = data;
    
    // Create user in Firebase Auth
    const userRecord = await auth().createUser({
      email,
      password,
      displayName: username
    });
    
    // Create user document in Firestore
    const userDoc = {
      uid: userRecord.uid,
      username,
      email,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp(),
      isActive: true,
      settings: {
        preferredAIProvider: "openai",
        enableFallbackProviders: true,
        notifications: true,
        privacy: {
          shareData: false,
          allowAnalytics: true
        }
      }
    };
    
    await db.collection("users").doc(userRecord.uid).set(userDoc);
    
    return {
      success: true,
      uid: userRecord.uid,
      message: "User registered successfully"
    };
  } catch (error) {
    console.error("Registration error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Registration failed",
      error.message
    );
  }
});

// User login (handled by client-side Firebase Auth, but we can add custom claims)
export const addCustomClaims = functions.https.onCall(async (data, context) => {
  try {
    // Verify the caller is authenticated
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const uid = context.auth.uid;
    
    // Add custom claims
    await auth().setCustomUserClaims(uid, {
      role: "user",
      permissions: ["read", "write", "delete"]
    });
    
    return {
      success: true,
      message: "Custom claims added successfully"
    };
  } catch (error) {
    console.error("Custom claims error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to add custom claims",
      error.message
    );
  }
});

// Get user profile
export const getProfile = functions.https.onCall(async (data, context) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const uid = context.auth.uid;
    const userDoc = await db.collection("users").doc(uid).get();
    
    if (!userDoc.exists) {
      throw new functions.https.HttpsError(
        "not-found",
        "User profile not found"
      );
    }
    
    return {
      success: true,
      profile: userDoc.data()
    };
  } catch (error) {
    console.error("Get profile error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to get user profile",
      error.message
    );
  }
});

// Update user profile
export const updateProfile = functions.https.onCall(async (data, context) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const uid = context.auth.uid;
    const updates = data;
    
    // Remove sensitive fields that shouldn't be updated directly
    delete updates.uid;
    delete updates.createdAt;
    
    updates.updatedAt = admin.firestore.FieldValue.serverTimestamp();
    
    await db.collection("users").doc(uid).update(updates);
    
    return {
      success: true,
      message: "Profile updated successfully"
    };
  } catch (error) {
    console.error("Update profile error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to update user profile",
      error.message
    );
  }
});

// Delete user account
export const deleteAccount = functions.https.onCall(async (data, context) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const uid = context.auth.uid;
    
    // Delete user document from Firestore
    await db.collection("users").doc(uid).delete();
    
    // Delete all user data (cascade delete)
    const collections = [
      "individuals",
      "families", 
      "events",
      "media",
      "knowledge",
      "faces",
      "ingestion",
      "conversations"
    ];
    
    for (const collectionName of collections) {
      const snapshot = await db
        .collection(collectionName)
        .where("userId", "==", uid)
        .get();
      
      const batch = db.batch();
      snapshot.forEach(doc => {
        batch.delete(doc.ref);
      });
      
      await batch.commit();
    }
    
    // Delete user from Firebase Auth
    await auth().deleteUser(uid);
    
    return {
      success: true,
      message: "Account deleted successfully"
    };
  } catch (error) {
    console.error("Delete account error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to delete account",
      error.message
    );
  }
});

export const authFunctions = {
  register,
  addCustomClaims,
  getProfile,
  updateProfile,
  deleteAccount
};
