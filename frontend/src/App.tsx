import { useCallback, useEffect, useState } from "react";
import { Bot, Menu } from "lucide-react";

import { api, setClientApiKey, type ChatResponse, type Conversation, type DocumentItem } from "./api/client";
import { ChatWindow } from "./components/ChatWindow";
import { Sidebar } from "./components/Sidebar";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  citations?: ChatResponse["citations"];
  agentName?: string;
  createdAt?: string;
}

export default function App() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [apiKey, setApiKey] = useState(() => localStorage.getItem("assistant_api_key") ?? "");
  const [role, setRole] = useState<string | null>(null);

  const refreshConversations = useCallback(async () => {
    try {
      setConversations(await api.listConversations());
    } catch {
      // 后台刷新失败不打断界面
    }
  }, []);

  const refreshDocuments = useCallback(async () => {
    try {
      const data = await api.listDocuments();
      setDocuments(data.items);
    } catch {
      // 后台刷新失败不打断界面
    }
  }, []);

  const refreshRole = useCallback(async () => {
    try {
      const data = await api.me();
      setRole(data.role);
    } catch {
      setRole(null);
    }
  }, []);

  useEffect(() => {
    if (apiKey) {
      setClientApiKey(apiKey);
      void refreshRole();
    }
    void refreshConversations();
    void refreshDocuments();
    const timer = window.setInterval(() => void refreshDocuments(), 3000);
    return () => window.clearInterval(timer);
  }, [apiKey, refreshConversations, refreshDocuments, refreshRole]);

  const openConversation = useCallback(async (conversationId: string) => {
    setActiveConversationId(conversationId);
    setSidebarOpen(false);
    setError(null);
    try {
      const history = await api.listMessages(conversationId);
      setMessages(
        history.map((message) => ({
          role: message.role as "user" | "assistant",
          content: message.content,
          citations: message.citations,
          agentName: message.agent_name ?? undefined,
          createdAt: message.created_at,
        }))
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : "加载会话失败");
    }
  }, []);

  const newConversation = useCallback(() => {
    setActiveConversationId(null);
    setMessages([]);
    setError(null);
    setSidebarOpen(false);
  }, []);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim() || loading) return;
      setError(null);
      setMessages((current) => [...current, { role: "user", content: text }]);
      setLoading(true);
      try {
        const response = await api.chat(text, activeConversationId ?? undefined);
        setActiveConversationId(response.conversation_id);
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content: response.answer,
            citations: response.citations,
            agentName: response.agent_name,
          },
        ]);
        void refreshConversations();
      } catch (e) {
        setError(e instanceof Error ? e.message : "请求失败，请稍后重试");
      } finally {
        setLoading(false);
      }
    },
    [activeConversationId, loading, refreshConversations]
  );

  const handleUpload = useCallback(
    async (file: File) => {
      setUploading(true);
      setError(null);
      try {
        await api.uploadDocument(file);
        await refreshDocuments();
      } catch (e) {
        setError(e instanceof Error ? e.message : "上传失败");
      } finally {
        setUploading(false);
      }
    },
    [refreshDocuments]
  );

  const handleDelete = useCallback(
    async (documentId: string) => {
      try {
        await api.deleteDocument(documentId);
        await refreshDocuments();
      } catch (e) {
        setError(e instanceof Error ? e.message : "删除失败");
      }
    },
    [refreshDocuments]
  );

  const handleApiKeyChange = useCallback(
    (key: string) => {
      setApiKey(key);
      localStorage.setItem("assistant_api_key", key);
      setClientApiKey(key);
      void refreshRole();
    },
    [refreshRole]
  );

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        documents={documents}
        uploading={uploading}
        apiKey={apiKey}
        role={role}
        onApiKeyChange={handleApiKeyChange}
        open={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNew={newConversation}
        onSelect={openConversation}
        onUpload={handleUpload}
        onDelete={handleDelete}
      />
      <main className="main">
        <header className="chat-header">
          <button
            className="menu-button"
            onClick={() => setSidebarOpen(true)}
            aria-label="打开菜单"
          >
            <Menu size={18} />
          </button>
          <div className="chat-header-title">
            <Bot size={18} />
            <span>企业知识库智能助手</span>
          </div>
        </header>
        <ChatWindow messages={messages} loading={loading} error={error} onSend={sendMessage} />
      </main>
    </div>
  );
}
