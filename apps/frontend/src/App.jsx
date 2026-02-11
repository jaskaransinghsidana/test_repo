import { useEffect, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

const buildApiUrl = (path) => {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE.replace(/\/+$/, '')}${normalizedPath}`;
};

function App() {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState([
    { role: 'assistant', content: 'Hi! I can plan tasks with LangGraph, use MCP tools, and summarize with an LLM.' },
  ]);
  const [plan, setPlan] = useState(null);
  const [tools, setTools] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(buildApiUrl('/mcp/tools'))
      .then((res) => {
        if (!res?.ok) {
          throw new Error('Failed to load tools');
        }

        return res.json();
      })
      .then((data) => setTools(data.tools || []))
      .catch(() => setTools([]));
  }, []);

  const sendMessage = async (event) => {
    event.preventDefault();
    if (!message.trim()) return;

    const userMessage = message.trim();
    setMessage('');
    setHistory((prev) => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await fetch(buildApiUrl('/chat'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage }),
      });

      if (!response?.ok) {
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      setHistory((prev) => [...prev, { role: 'assistant', content: data.reply }]);
      setPlan(data.plan);
    } catch {
      setHistory((prev) => [...prev, { role: 'assistant', content: 'Sorry, backend is unavailable.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="layout">
      <aside className="panel">
        <h2>MCP Tools</h2>
        <ul>
          {tools.map((tool) => (
            <li key={tool.name}>
              <strong>{tool.name}</strong>
              <p>{tool.description}</p>
            </li>
          ))}
        </ul>
      </aside>

      <main className="chat-shell">
        <header>
          <h1>Agentic Solution Console</h1>
          <p>Plan → Task Creation → Execution with MCP integration</p>
        </header>

        <section className="messages">
          {history.map((entry, idx) => (
            <div key={idx} className={`bubble ${entry.role}`}>
              {entry.content}
            </div>
          ))}
          {loading && <div className="bubble assistant">Thinking and executing plan...</div>}
        </section>

        <form onSubmit={sendMessage} className="composer">
          <input
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Ask me to research or calculate with tools..."
          />
          <button type="submit" disabled={loading}>Send</button>
        </form>
      </main>

      <aside className="panel">
        <h2>Execution Plan</h2>
        {!plan ? (
          <p>No plan yet. Send a message to generate tasks.</p>
        ) : (
          <ol>
            {plan.tasks.map((task) => (
              <li key={task.id}>
                <div className="task-title">{task.title}</div>
                <div className={`status ${task.status}`}>{task.status}</div>
                {task.tool_name && <small>Tool: {task.tool_name}</small>}
              </li>
            ))}
          </ol>
        )}
      </aside>
    </div>
  );
}

export default App;
