import { useEffect, useRef, useState, type ChangeEvent } from "react";
import { FileText, MessageSquare, Plus, Trash2, Upload } from "lucide-react";

import { Conversation, DocumentItem } from "../api/client";

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string | null;
  documents: DocumentItem[];
  uploading: boolean;
  apiKey: string;
  role: string | null;
  onApiKeyChange: (key: string) => void;
  open: boolean;
  onClose: () => void;
  onNew: () => void;
  onSelect: (id: string) => void;
  onUpload: (file: File) => void;
  onDelete: (id: string) => void;
}

const STATUS_LABEL: Record<string, string> = {
  uploaded: "等待处理",
  processing: "处理中",
  ready: "就绪",
  failed: "失败",
};

export function Sidebar({
  conversations,
  activeConversationId,
  documents,
  uploading,
  apiKey,
  role,
  onApiKeyChange,
  open,
  onClose,
  onNew,
  onSelect,
  onUpload,
  onDelete,
}: SidebarProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [keyDraft, setKeyDraft] = useState(apiKey);

  useEffect(() => {
    setKeyDraft(apiKey);
  }, [apiKey]);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onUpload(file);
    }
    event.target.value = "";
  };

  return (
    <>
      <div className={`sidebar-backdrop ${open ? "visible" : ""}`} onClick={onClose} />
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="sidebar-brand">
          <div className="brand-mark">
            <MessageSquare size={18} />
          </div>
          <div>
            <div className="brand-name">企业知识库助手</div>
            <div className="brand-sub">{documents.length} 篇文档</div>
          </div>
        </div>

        <button className="new-chat-button" onClick={onNew}>
          <Plus size={16} />
          <span>新建对话</span>
        </button>

        <section className="sidebar-section">
          <h2 className="sidebar-heading">对话</h2>
          <div className="conversation-list">
            {conversations.length === 0 && <div className="empty-hint">暂无对话</div>}
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                className={`conversation-item ${activeConversationId === conversation.id ? "active" : ""}`}
                onClick={() => onSelect(conversation.id)}
              >
                <span className="conversation-title">{conversation.title || "未命名对话"}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="sidebar-section knowledge-section">
          <div className="knowledge-heading-row">
            <h2 className="sidebar-heading">知识库</h2>
            <button
              className="icon-button"
              disabled={uploading}
              onClick={() => fileInputRef.current?.click()}
              title="上传文档"
              aria-label="上传文档"
            >
              <Upload size={16} />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.md,.txt,.markdown"
              hidden
              onChange={handleFileChange}
            />
          </div>
          <div className="document-list">
            {documents.length === 0 && <div className="empty-hint">暂无文档</div>}
            {documents.map((document) => (
              <div key={document.id} className="document-item">
                <FileText size={15} className="document-icon" />
                <div className="document-info">
                  <div className="document-name" title={document.filename}>
                    {document.filename}
                  </div>
                  <div className={`document-status status-${document.status}`}>
                    {STATUS_LABEL[document.status] ?? document.status}
                  </div>
                </div>
                {role === "admin" && (
                  <button
                    className="delete-button"
                    onClick={() => onDelete(document.id)}
                    title="删除文档"
                    aria-label="删除文档"
                  >
                    <Trash2 size={14} />
                  </button>
                )}
              </div>
            ))}
          </div>
        </section>

        <section className="sidebar-section auth-section">
          <h2 className="sidebar-heading">访问权限</h2>
          <div className="auth-row">
            <input
              className="auth-input"
              type="password"
              value={keyDraft}
              onChange={(event) => setKeyDraft(event.target.value)}
              placeholder="API Key"
            />
            <button className="auth-save" onClick={() => onApiKeyChange(keyDraft.trim())}>
              保存
            </button>
          </div>
          <div className={`role-badge ${role === "admin" ? "admin" : role === "user" ? "user" : ""}`}>
            {role === "admin" ? "管理员" : role === "user" ? "普通用户" : "未配置 Key"}
          </div>
        </section>
      </aside>
    </>
  );
}
