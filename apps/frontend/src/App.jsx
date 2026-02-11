import { useEffect, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

function App() {
  const [message, setMessage] = useState('');
  const [history, setHistory] = useState([
    { role: 'assistant', content: 'Hi! I can plan tasks, use MCP tools, and execute agent workflows.' },
  ]);
  const [plan, setPlan] = useState(null);
  const [tools, setTools] = useState([]);
  const [examples, setExamples] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/mcp/tools`)
      .then((res) => res.json())
      .then((data) => setTools(data.tools || []))
      .catch(() => setTools([]));

    fetch(`${API_BASE}/mcp/examples`)
      .then((res) => res.json())
      .then((data) => setExamples(data.examples || []))
      .catch(() => setExamples([]));
  }, []);

  const sendMessage = async (event, presetMessage = null) => {
    event?.preventDefault?.();
    const outgoing = (presetMessage || message).trim();
    if (!outgoing) return;

    if (!presetMessage) {
      setMessage('');
    }

    setHistory((prev) => [...prev, { role: 'user', content: outgoing }]);
    setLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: outgoing }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        const detail = payload.detail || `Backend returned HTTP ${response.status}`;
        throw new Error(detail);
      }

      const data = await response.json();
      setHistory((prev) => [...prev, { role: 'assistant', content: data.reply }]);
      setPlan(data.plan);
    } catch (error) {
      const detail = error instanceof Error ? error.message : 'Backend is unavailable.';
      setHistory((prev) => [...prev, { role: 'assistant', content: `Request failed: ${detail}` }]);
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

        <h3>MCP Examples</h3>
        {examples.length === 0 ? (
          <p className="small-note">No examples available.</p>
        ) : (
          <ul className="examples-list">
            {examples.map((example) => (
              <li key={example.title}>
                <strong>{example.title}</strong>
                <p>{example.goal}</p>
                <button
                  type="button"
                  className="example-btn"
                  disabled={loading}
                  onClick={(event) => sendMessage(event, example.chat_prompt)}
                >
                  Run: {example.chat_prompt}
                </button>
              </li>
            ))}
          </ul>
        )}
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
