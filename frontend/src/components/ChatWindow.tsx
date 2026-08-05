import { useEffect, useRef, useState } from "react";
import { Send } from "lucide-react";

import { ChatMessage } from "../App";
import { MessageBubble } from "./MessageBubble";

interface ChatWindowProps {
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  onSend: (text: string) => void;
}

export function ChatWindow({ messages, loading, error, onSend }: ChatWindowProps) {
  const [draft, setDraft] = useState("");
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const submit = () => {
    const text = draft.trim();
    if (!text || loading) return;
    onSend(text);
    setDraft("");
  };

  return (
    <div className="chat-window">
      <div className="messages">
        {messages.length === 0 && !loading && (
          <div className="welcome-panel">
            <div className="welcome-title">开始新的对话</div>
          </div>
        )}
        {messages.map((message, index) => (
          <MessageBubble key={index} message={message} />
        ))}
        {loading && (
          <div className="message assistant">
            <div className="typing-dots">
              <span />
              <span />
              <span />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="input-bar">
        <textarea
          className="chat-input"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              submit();
            }
          }}
          placeholder="输入你的问题"
          rows={2}
        />
        <button
          className="send-button"
          onClick={submit}
          disabled={!draft.trim() || loading}
          aria-label="发送"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
}
