"use client";
import { useState, useRef, useEffect } from "react";

// 🔥 [핵심] Render 배포 주소 적용 (끝에 /api/coach 필수)
const API_URL = "https://project-sys-j.onrender.com/api/coach";

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false); // 채팅창 열림/닫힘 상태
  const [input, setInput] = useState("");      // 사용자 입력값
  const [messages, setMessages] = useState<{ role: "user" | "ai"; text: string }[]>([
    { role: "ai", text: "안녕하세요! AI 자소서 코치입니다. 자소서 내용이나 면접 고민을 입력해주시면 분석해 드립니다." }
  ]);
  const [isLoading, setIsLoading] = useState(false); // 로딩 상태
  const scrollRef = useRef<HTMLDivElement>(null);    // 스크롤 자동 이동용

  // 메시지가 추가되거나 창이 열릴 때 스크롤을 맨 아래로 이동
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // 1. 사용자 메시지 화면에 즉시 표시
    const userMsg = input;
    setMessages((prev) => [...prev, { role: "user", text: userMsg }]);
    setInput("");
    setIsLoading(true);

    try {
      // 2. FastAPI 서버(Render)로 전송
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: userMsg }), // 백엔드 스키마와 일치해야 함
      });
      
      if (!res.ok) {
        throw new Error(`Server Error: ${res.status}`);
      }

      const data = await res.json();
      
      // 3. AI 응답 화면에 표시
      setMessages((prev) => [...prev, { role: "ai", text: data.answer }]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [...prev, { role: "ai", text: "죄송합니다. 서버 연결에 문제가 발생했습니다. 잠시 후 다시 시도해주세요." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end font-sans">
      
      {/* 🟢 채팅창 본체 (isOpen이 true일 때만 보임) */}
      {isOpen && (
        <div className="mb-4 w-[360px] h-[550px] bg-black/90 border border-cyan-500 rounded-2xl shadow-[0_0_25px_rgba(6,182,212,0.6)] flex flex-col overflow-hidden backdrop-blur-md animate-fade-in-up transition-all duration-300">
          
          {/* 1. 헤더 */}
          <div className="bg-cyan-950/80 p-4 border-b border-cyan-500/50 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="text-xl">🎓</span>
              <span className="text-cyan-400 font-bold tracking-wider drop-shadow-md">Job-Navigator</span>
            </div>
            <button 
              onClick={() => setIsOpen(false)} 
              className="text-gray-400 hover:text-white hover:rotate-90 transition-transform duration-200"
            >
              ✕
            </button>
          </div>

          {/* 2. 메시지 리스트 영역 */}
          <div ref={scrollRef} className="flex-1 p-4 overflow-y-auto space-y-4 scrollbar-thin scrollbar-thumb-cyan-900 scrollbar-track-transparent">
            {messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[85%] p-3 text-sm leading-relaxed rounded-2xl shadow-sm ${
                  msg.role === "user" 
                    ? "bg-cyan-700 text-white rounded-tr-none" 
                    : "bg-gray-800 text-gray-200 border border-gray-700 rounded-tl-none"
                }`}>
                  {/* 줄바꿈 처리를 위해 whitespace-pre-wrap 적용 */}
                  <p className="whitespace-pre-wrap">{msg.text}</p>
                </div>
              </div>
            ))}
            
            {/* 로딩 인디케이터 */}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-800 border border-gray-700 p-3 rounded-2xl rounded-tl-none text-cyan-500 text-xs flex items-center gap-2 animate-pulse">
                  <span>AI가 분석 중입니다...</span>
                  <span className="animate-spin">⏳</span>
                </div>
              </div>
            )}
          </div>

          {/* 3. 입력창 영역 */}
          <div className="p-3 bg-gray-900/90 border-t border-gray-700 flex gap-2">
            <input
              className="flex-1 bg-gray-800 text-white text-sm rounded-full px-4 py-3 focus:outline-none focus:ring-2 focus:ring-cyan-500 placeholder-gray-500 transition-all"
              placeholder="내용을 입력하세요..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()}
            />
            <button 
              onClick={sendMessage}
              disabled={isLoading}
              className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 disabled:opacity-50 text-white rounded-full w-12 h-12 flex items-center justify-center transition-all shadow-lg hover:shadow-cyan-500/50"
            >
              ➤
            </button>
          </div>
        </div>
      )}

      {/* 🟢 둥둥 떠있는 버튼 (Floating Action Button) */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`w-16 h-16 rounded-full shadow-[0_0_20px_rgba(6,182,212,0.6)] flex items-center justify-center text-3xl transition-all duration-300 hover:scale-110 active:scale-95 ${
            isOpen ? "bg-gray-700 rotate-45" : "bg-gradient-to-r from-cyan-500 to-blue-600 hover:shadow-cyan-400/50"
        }`}
      >
        {isOpen ? "➕" : "🤖"}
      </button>
    </div>
  );
}