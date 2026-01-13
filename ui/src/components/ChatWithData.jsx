import { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, X, ChevronRight, ChevronLeft } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

const ChatWithData = ({ apiEndpoint = 'http://localhost:11434/api/generate' }) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [contextData, setContextData] = useState([]);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleInputChange = (e) => {
    setInput(e.target.value);
  };

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'llama3.3',
          prompt: formatPrompt(input, contextData),
          stream: true,
        }),
      });

      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiResponse = '';
      let done = false;

      while (!done) {
        const { value, done: streamDone } = await reader.read();
        done = streamDone;
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('{')) {
            try {
              const parsed = JSON.parse(line);
              if (parsed.response) {
                aiResponse += parsed.response;
                setMessages((prev) => {
                  const lastMessage = prev[prev.length - 1];
                  if (lastMessage && lastMessage.role === 'assistant') {
                    return [...prev.slice(0, -1), { ...lastMessage, content: aiResponse }];
                  }
                  return [...prev, { role: 'assistant', content: aiResponse }];
                });
              }
              if (parsed.done) {
                done = true;
                break;
              }
            } catch (e) {
              console.error('JSON parse error:', e, line);
            }
          }
        }
      }

      // Fetch context data after AI response (mock for now)
      setContextData(mockContextData(input));
    } catch (error) {
      console.error('Error fetching AI response:', error);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Error: Unable to fetch response. Please try again.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrompt = (userInput, context) => {
    const contextText = context.length > 0
      ? context.map((c) => `Event: ${c.event}, Location: ${c.location}, Date: ${c.date}`).join('\n')
      : 'No specific context available.';
    return `You are an NNVCD AI Expert. Use the following historical data to answer the user's question accurately.\n\nHISTORICAL CONTEXT:\n${contextText}\n\nUSER QUESTION: ${userInput}\n\nEXPERT ANALYSIS:`;
  };

  const mockContextData = (query) => {
    // Mock function to simulate fetching ACLED data based on query
    return [
      { event: 'Armed Clash', location: 'Zamfara', date: '2023-01-15' },
      { event: 'Kidnapping', location: 'Kaduna', date: '2023-02-20' },
      { event: 'Banditry', location: 'Borno', date: '2023-03-05' },
    ];
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="flex flex-col bg-gray-800/80 backdrop-blur-sm rounded-lg shadow-lg overflow-hidden relative border border-gray-700" style={{ minHeight: '500px', height: '500px' }}>
      {/* Chat Header */}
      <div className="flex items-center justify-between p-3 bg-gray-700/50 border-b border-gray-600 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Bot size={20} className="text-cyan-400" />
          <h3 className="text-white text-base font-semibold">Chat with Data</h3>
        </div>
        <button
          onClick={toggleSidebar}
          className="text-gray-400 hover:text-white transition-colors p-1 hover:bg-gray-600/50 rounded"
          title={isSidebarOpen ? 'Hide Context' : 'Show Context'}
        >
          {isSidebarOpen ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-1 min-h-0 relative">
        {/* Chat Messages */}
        <div className={`flex flex-col ${isSidebarOpen ? 'w-full' : 'w-full'} transition-all duration-300`}>
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-3"
            style={{ minHeight: '300px' }}
          >
            {messages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-400">
                <Bot size={48} className="mb-3 text-cyan-400/50" />
                <p className="text-sm text-center">Ask about conflict trends in Nigeria...</p>
                <p className="text-xs text-gray-500 mt-2">Powered by ACLED data</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div
                  key={index}
                  className={`flex items-start gap-2 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
                >
                  <div className={`flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-blue-500' : 'bg-cyan-500/20 border border-cyan-500/50'}`}>
                    {msg.role === 'user' ? <User size={16} className="text-white" /> : <Bot size={16} className="text-cyan-400" />}
                  </div>
                  <div
                    className={`flex-1 p-3 rounded-lg text-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-700/80 text-gray-100 border border-gray-600'}`}
                    style={{ maxWidth: '85%' }}
                  >
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      rehypePlugins={[rehypeRaw]}
                      components={{
                        table: ({ node, ...props }) => (
                          <table className="border-collapse border border-gray-500 w-full my-2 text-xs" {...props} />
                        ),
                        th: ({ node, ...props }) => (
                          <th className="border border-gray-400 p-2 bg-gray-600 text-left" {...props} />
                        ),
                        td: ({ node, ...props }) => (
                          <td className="border border-gray-400 p-2" {...props} />
                        ),
                        h3: ({ node, ...props }) => (
                          <h3 className="font-bold text-base mt-2 mb-1" {...props} />
                        ),
                        h4: ({ node, ...props }) => (
                          <h4 className="font-semibold text-sm mt-1 mb-1" {...props} />
                        ),
                        p: ({ node, ...props }) => (
                          <p className="mb-2" {...props} />
                        ),
                        ul: ({ node, ...props }) => (
                          <ul className="list-disc list-inside mb-2" {...props} />
                        ),
                        ol: ({ node, ...props }) => (
                          <ol className="list-decimal list-inside mb-2" {...props} />
                        ),
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex items-start gap-2">
                <div className="flex-shrink-0 w-7 h-7 rounded-full flex items-center justify-center bg-cyan-500/20 border border-cyan-500/50">
                  <Bot size={16} className="text-cyan-400 animate-pulse" />
                </div>
                <div className="flex-1 p-3 rounded-lg text-sm bg-gray-700/80 text-gray-100 border border-gray-600">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="p-3 border-t border-gray-600 bg-gray-800/50 flex-shrink-0">
            <div className="flex items-center gap-2 bg-gray-700/50 rounded-lg p-2 border border-gray-600 focus-within:border-cyan-500 transition-colors">
              <input
                type="text"
                value={input}
                onChange={handleInputChange}
                onKeyPress={handleKeyPress}
                placeholder="Ask about conflict trends, patterns, or specific regions..."
                className="flex-1 bg-transparent text-white outline-none text-sm placeholder-gray-400"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !input.trim()}
                className={`p-2 rounded-lg transition-colors flex-shrink-0 ${isLoading || !input.trim() ? 'text-gray-500 cursor-not-allowed' : 'text-cyan-400 hover:bg-cyan-500/20 hover:text-cyan-300'}`}
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>

        {/* Context Sidebar */}
        <div
          className={`absolute right-0 top-0 bottom-0 bg-gray-800/95 border-l border-gray-600 shadow-xl transition-all duration-300 overflow-hidden ${isSidebarOpen ? 'w-[280px]' : 'w-0'}`}
        >
          <div className="p-3 h-full overflow-y-auto">
            <div className="flex items-center gap-2 mb-3">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse"></div>
              <h4 className="text-white font-semibold text-sm">ACLED Context</h4>
            </div>
            {contextData.length === 0 ? (
              <div className="text-gray-400 text-xs leading-relaxed">
                <p className="mb-2">No context loaded yet.</p>
                <p>Ask a question to see relevant historical conflict data from the ACLED database.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {contextData.map((item, index) => (
                  <div key={index} className="bg-gray-700/60 p-2 rounded border border-gray-600 text-xs hover:border-cyan-500/50 transition-colors">
                    <div className="font-semibold text-cyan-400 mb-1 flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></div>
                      {item.event}
                    </div>
                    <div className="text-gray-300 mb-0.5">📍 {item.location}</div>
                    <div className="text-gray-400">📅 {item.date}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWithData;
