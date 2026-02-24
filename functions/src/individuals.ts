import * as functions from "firebase-functions";
import { db } from "./index";

// Create individual
export const createIndividual = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const userId = context.auth.uid;
    const individualData = {
      ...data,
      userId,
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    };
    
    const docRef = await db
      .collection("users")
      .doc(userId)
      .collection("individuals")
      .add(individualData);
    
    return {
      success: true,
      id: docRef.id,
      message: "Individual created successfully"
    };
  } catch (error) {
    console.error("Create individual error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to create individual",
      (error as Error).message
    );
  }
});

// Get individual by ID
export const getIndividual = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const userId = context.auth.uid;
    const { individualId } = data;
    
    const doc = await db
      .collection("users")
      .doc(userId)
      .collection("individuals")
      .doc(individualId)
      .get();
    
    if (!doc.exists) {
      throw new functions.https.HttpsError(
        "not-found",
        "Individual not found"
      );
    }
    
    return {
      success: true,
      individual: { id: doc.id, ...doc.data() }
    };
  } catch (error) {
    console.error("Get individual error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to get individual",
      (error as Error).message
    );
  }
});

// List individuals with pagination and filtering
export const listIndividuals = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const userId = context.auth.uid;
    const {
      limit = 20,
      offset = 0,
      sortBy = "createdAt",
      sortOrder = "desc",
      search = "",
      filters = {}
    } = data;
    
    let query = db
      .collection("users")
      .doc(userId)
      .collection("individuals") as any;
    
    // Apply filters
    if (filters.surname) {
      query = query.where("surname", "==", filters.surname);
    }
    
    if (filters.birthDateRange) {
      query = query
        .where("birthDate", ">=", filters.birthDateRange.start)
        .where("birthDate", "<=", filters.birthDateRange.end);
    }
    
    if (filters.sex) {
      query = query.where("sex", "==", filters.sex);
    }
    
    // Apply search
    if (search) {
      query = query
        .where("givenNames", ">=", search)
        .where("givenNames", "<=", search + "\uf8ff");
    }
    
    // Apply sorting and pagination
    query = query
      .orderBy(sortBy, sortOrder)
      .limit(limit)
      .offset(offset);
    
    const snapshot = await query.get();
    const individuals = snapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }));
    
    return {
      success: true,
      individuals,
      hasMore: individuals.length === limit
    };
  } catch (error) {
    console.error("List individuals error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to list individuals",
      (error as Error).message
    );
  }
});

// Update individual
export const updateIndividual = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const userId = context.auth.uid;
    const { individualId, updates } = data;
    
    // Remove fields that shouldn't be updated directly
    delete updates.userId;
    delete updates.createdAt;
    
    updates.updatedAt = admin.firestore.FieldValue.serverTimestamp();
    
    await db
      .collection("users")
      .doc(userId)
      .collection("individuals")
      .doc(individualId)
      .update(updates);
    
    return {
      success: true,
      message: "Individual updated successfully"
    };
  } catch (error) {
    console.error("Update individual error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to update individual",
      (error as Error).message
    );
  }
});

// Delete individual
export const deleteIndividual = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const userId = context.auth.uid;
    const { individualId } = data;
    
    // Check if individual is referenced in families
    const familiesSnapshot = await db
      .collection("users")
      .doc(userId)
      .collection("families")
      .where("husbandId", "==", individualId)
      .get();
    
    if (!familiesSnapshot.empty) {
      throw new functions.https.HttpsError(
        "failed-precondition",
        "Cannot delete individual: referenced in families as husband"
      );
    }
    
    const wivesSnapshot = await db
      .collection("users")
      .doc(userId)
      .collection("families")
      .where("wifeId", "==", individualId)
      .get();
    
    if (!wivesSnapshot.empty) {
      throw new functions.https.HttpsError(
        "failed-precondition",
        "Cannot delete individual: referenced in families as wife"
      );
    }
    
    await db
      .collection("users")
      .doc(userId)
      .collection("individuals")
      .doc(individualId)
      .delete();
    
    return {
      success: true,
      message: "Individual deleted successfully"
    };
  } catch (error) {
    console.error("Delete individual error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to delete individual",
      (error as Error).message
    );
  }
});

// Search individuals by name
export const searchIndividuals = functions.https.onCall(async (data: any, context: any) => {
  try {
    if (!context.auth) {
      throw new functions.https.HttpsError(
        "unauthenticated",
        "User must be authenticated"
      );
    }
    
    const userId = context.auth.uid;
    const { query: searchQuery, limit = 10 } = data;
    
    // Search by given names
    const givenNamesSnapshot = await db
      .collection("users")
      .doc(userId)
      .collection("individuals")
      .where("givenNames", ">=", searchQuery)
      .where("givenNames", "<=", searchQuery + "\uf8ff")
      .limit(limit)
      .get();
    
    // Search by surname
    const surnameSnapshot = await db
      .collection("users")
      .doc(userId)
      .collection("individuals")
      .where("surname", ">=", searchQuery)
      .where("surname", "<=", searchQuery + "\uf8ff")
      .limit(limit)
      .get();
    
    // Combine results and remove duplicates
    const results = new Map();
    
    givenNamesSnapshot.docs.forEach(doc => {
      results.set(doc.id, { id: doc.id, ...doc.data() });
    });
    
    surnameSnapshot.docs.forEach(doc => {
      results.set(doc.id, { id: doc.id, ...doc.data() });
    });
    
    return {
      success: true,
      individuals: Array.from(results.values()).slice(0, limit)
    };
  } catch (error) {
    console.error("Search individuals error:", error);
    throw new functions.https.HttpsError(
      "internal",
      "Failed to search individuals",
      (error as Error).message
    );
  }
});

export const individualFunctions = {
  createIndividual,
  getIndividual,
  listIndividuals,
  updateIndividual,
  deleteIndividual,
  searchIndividuals
};
