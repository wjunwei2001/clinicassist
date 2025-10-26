"use client";

import { useState, useRef, useEffect } from "react";
import Sidebar from "@/components/Sidebar";
import ProgressBar from "@/components/ProgressBar";
import { Message, ChatResponse, PatientState } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [state, setState] = useState<PatientState>({});
  const [phase, setPhase] = useState<string>("Not started");
  const [isComplete, setIsComplete] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (sessionId && !isComplete) {
      inputRef.current?.focus();
    }
  }, [sessionId, isComplete]);

  const startConversation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      });

      if (!response.ok) {
        throw new Error("Failed to start conversation");
      }

      const data: ChatResponse = await response.json();
      setSessionId(data.session_id);
      setMessages([
        {
          role: "assistant",
          content: data.assistant_message || "Hello! Let's get started.",
        },
      ]);
      setState(data.state);
      setPhase(data.phase);
      setIsComplete(data.is_complete);
    } catch (error) {
      console.error("Error starting conversation:", error);
      alert("Failed to start conversation. Make sure the backend is running.");
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || isLoading) return;

    const userMessage: Message = {
      role: "user",
      content: inputMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);
    inputRef.current?.focus();

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/reply`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: inputMessage,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data: ChatResponse = await response.json();

      if (data.assistant_message) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant" as const,
            content: data.assistant_message as string,
          },
        ]);
      }

      setState(data.state);
      setPhase(data.phase);
      setIsComplete(data.is_complete);
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant" as const,
          content: "Sorry, there was an error processing your message.",
        },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const resetConversation = () => {
    setSessionId(null);
    setMessages([]);
    setInputMessage("");
    setState({});
    setPhase("Not started");
    setIsComplete(false);
  };

  return (
    <div className="flex h-screen bg-white dark:bg-gray-950">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
          <div className="px-4 py-4">
            <div className="flex items-center justify-between max-w-4xl mx-auto mb-4">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                ClinicAssist
              </h1>
              {sessionId && (
                <button
                  onClick={resetConversation}
                  className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-gray-100 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                >
                  New Session
                </button>
              )}
            </div>
            {sessionId && (
              <div className="pb-4">
                <ProgressBar phase={phase} isComplete={isComplete} />
              </div>
            )}
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="max-w-4xl mx-auto">
            {!sessionId ? (
              <div className="flex flex-col items-center justify-center h-full min-h-[400px]">
                <div className="text-center mb-8">
                  <h2 className="text-3xl font-bold text-gray-900 dark:text-gray-100 mb-4">
                    Welcome to ClinicAssist
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400 mb-8 max-w-md">
                    Your AI-powered clinical assistant for patient intake and
                    triage. Click the button below to begin.
                  </p>
                  <button
                    onClick={startConversation}
                    disabled={isLoading}
                    className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isLoading ? "Starting..." : "Start Conversation"}
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4 pb-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${
                      message.role === "user" ? "justify-end" : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[80%] rounded-lg p-4 ${
                        message.role === "user"
                          ? "bg-blue-600 text-white"
                          : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
                      }`}
                    >
                      <div className="text-sm whitespace-pre-wrap">
                        {message.content}
                      </div>
                    </div>
                  </div>
                ))}
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                      </div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input Area */}
        {sessionId && !isComplete && (
          <div className="border-t border-gray-200 dark:border-gray-800 p-4 bg-white dark:bg-gray-900">
            <div className="max-w-4xl mx-auto flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={handleKeyPress}
                placeholder="Type your message..."
                ref={inputRef}
                enterKeyHint="send"
                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 disabled:opacity-50"
              />
              <button
                onClick={sendMessage}
                onMouseDown={(e) => e.preventDefault()}
                disabled={isLoading || !inputMessage.trim()}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Send
              </button>
            </div>
          </div>
        )}

        {isComplete && (
          <div className="border-t border-gray-200 dark:border-gray-800 p-4 bg-green-50 dark:bg-green-900/20">
            <div className="max-w-4xl mx-auto text-center">
              <p className="text-green-800 dark:text-green-200 font-medium">
                ✓ Conversation complete! All information has been collected.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Sidebar */}
      {sessionId && (
        <Sidebar state={state} phase={phase} isComplete={isComplete} />
      )}
    </div>
  );
}
