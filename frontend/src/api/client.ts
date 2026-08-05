export interface Citation {
  chunk_id: string;
  document_id: string;
  filename: string;
  page_number: number | null;
  excerpt: string;
  score: number;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  agent_name: string;
  citations: Citation[];
}

export interface UploadResult {
  id: string;
  filename: string;
  status: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  content_type: string;
  status: string;
  error: string | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  role: string;
  content: string;
  agent_name: string | null;
  citations: Citation[];
  created_at: string;
}

let apiKey: string | null = localStorage.getItem("assistant_api_key");

export function setClientApiKey(key: string): void {
  apiKey = key;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  if (apiKey) {
    headers.set("X-API-Key", apiKey);
  }
  const response = await fetch(path, {
    headers,
    ...init,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

export const api = {
  listDocuments: () => request<{ items: DocumentItem[] }>("/api/v1/documents"),
  uploadDocument: async (file: File) => {
    const form = new FormData();
    form.append("file", file);
    const headers: Record<string, string> = {};
    if (apiKey) {
      headers["X-API-Key"] = apiKey;
    }
    const response = await fetch("/api/v1/documents/upload", {
      method: "POST",
      body: form,
      headers,
    });
    if (!response.ok) {
      throw new Error(await response.text());
    }
    return response.json() as Promise<UploadResult>;
  },
  deleteDocument: (id: string) =>
    request<{ deleted: boolean }>(`/api/v1/documents/${id}`, { method: "DELETE" }),
  chat: (question: string, conversationId?: string) =>
    request<ChatResponse>("/api/v1/chat", {
      method: "POST",
      body: JSON.stringify({ question, conversation_id: conversationId ?? null }),
    }),
  listConversations: () => request<Conversation[]>("/api/v1/conversations"),
  listMessages: (conversationId: string) =>
    request<Message[]>(`/api/v1/conversations/${conversationId}/messages`),
  listAgents: () => request<{ name: string; description: string }[]>("/api/v1/agents"),
  me: () => request<{ role: string }>("/api/v1/me"),
};
