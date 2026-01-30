import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { nutritionAPI } from '../services/api';
import {
    Send,
    Bot,
    User,
    ChevronLeft,
    Zap,
    Utensils,
    BookOpen
} from 'lucide-react';
import './NutritionChat.css';

export default function NutritionChat() {
    const navigate = useNavigate();
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Olá! Sou seu Copiloto Neural de Nutrição. Como posso ajudar com seu plano alimentar hoje?' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || isLoading) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const response = await nutritionAPI.chat(input, messages);
            setMessages(prev => [...prev, { role: 'assistant', content: response.data.message }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'assistant', content: 'Ops, tive um erro ao falar com o servidor neural.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="nutrition-chat-page">
            <header className="chat-header">
                <button className="btn btn-ghost" onClick={() => navigate('/nutrition')}>
                    <ChevronLeft size={20} />
                </button>
                <div className="header-info">
                    <div className="ai-status">
                        <div className="status-dot pulsed"></div>
                        <strong>Copiloto Neural</strong>
                    </div>
                    <span className="api-model">Powered by GPT-4o</span>
                </div>
            </header>

            <div className="messages-container">
                {messages.map((msg, i) => (
                    <div key={i} className={`message-wrapper ${msg.role}`}>
                        <div className="avatar">
                            {msg.role === 'assistant' ? <Bot size={20} /> : <User size={20} />}
                        </div>
                        <div className="message-content">
                            {msg.content}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message-wrapper assistant">
                        <div className="avatar pulsed"><Zap size={20} /></div>
                        <div className="message-content typing">
                            O NeuralNutri está pensando...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div className="chat-suggestions">
                <button className="suggestion-chip" onClick={() => setInput('O que devo comer no pós-treino hoje?')}>
                    <Zap size={14} /> Pós-treino
                </button>
                <button className="suggestion-chip" onClick={() => setInput('Registre meu almoço: 200g de frango e 150g de arroz')}>
                    <Utensils size={14} /> Registrar Refeição
                </button>
                <button className="suggestion-chip" onClick={() => setInput('Crie um plano alimentar para melhorar minha resistência')}>
                    <BookOpen size={14} /> Sugerir Dieta
                </button>
            </div>

            <form className="chat-input-area" onSubmit={handleSend}>
                <input
                    type="text"
                    placeholder="Fale com sua IA nutricionista..."
                    value={input}
                    onChange={e => setInput(e.target.value)}
                />
                <button className="btn btn-primary" type="submit" disabled={isLoading}>
                    <Send size={20} />
                </button>
            </form>
        </div>
    );
}
