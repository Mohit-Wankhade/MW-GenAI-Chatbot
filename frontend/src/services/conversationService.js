import api from "./api";

function validateConversationId(id) {
  if (!id) {
    throw new Error("Conversation id is required.");
  }
}

export async function createConversation() {
  const response = await api.post("/conversation/new");
  return response.data;
}

export async function getConversations() {
  const response = await api.get("/conversation");
  return response.data;
}

export async function getConversation(id) {
  validateConversationId(id);

  const response = await api.get(`/conversation/${id}/messages`);
  return response.data;
}

export async function deleteConversation(id) {
  validateConversationId(id);

  const response = await api.delete(`/conversation/${id}`);
  return response.data;
}

export async function renameConversation(id, title) {
  validateConversationId(id);

  const cleanTitle = String(title || "").trim();

  if (!cleanTitle) {
    throw new Error("Conversation title cannot be empty.");
  }

  const response = await api.put(`/conversation/${id}`, {
    title: cleanTitle,
  });

  return response.data;
}

// Backward-compatible aliases in case older components use these names.
export const newConversation = createConversation;
export const getConversationMessages = getConversation;