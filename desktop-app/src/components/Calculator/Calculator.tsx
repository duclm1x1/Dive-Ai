import React, { useState } from 'react';
import './Calculator.css';

interface AlgorithmResult {
    status: string;
    data: any;
    meta: any;
    error?: string;
}

const Calculator: React.FC = () => {
    const [a, setA] = useState<string>('0');
    const [b, setB] = useState<string>('0');
    const [operation, setOperation] = useState<string>('add');
    const [result, setResult] = useState<AlgorithmResult | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    // Access the exposed API (assuming it's available via window.diveAPI or we fetch directly)
    // Since specific API bridge might not be set up for this yet, we'll use fetch directly to localhost:1879
    // In a real app, this should go through preload.js

    const executeCalculation = async () => {
        setLoading(true);
        setResult(null);

        try {
            const data = await window.diveAPI.gateway.request('/api/algorithm/execute', {
                name: 'calculator',
                inputs: {
                    operation,
                    a: parseFloat(a),
                    b: parseFloat(b)
                }
            });
            setResult(data);
        } catch (err: any) {
            setResult({
                status: 'failure',
                data: null,
                meta: {},
                error: err.message
            });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="calculator-container">
            <h2>Algorithm: Calculator</h2>
            <div className="calculator-controls">
                <div className="input-group">
                    <label>Value A:</label>
                    <input
                        type="number"
                        value={a}
                        onChange={(e) => setA(e.target.value)}
                    />
                </div>

                <div className="input-group">
                    <label>Operation:</label>
                    <select value={operation} onChange={(e) => setOperation(e.target.value)}>
                        <option value="add">Add (+)</option>
                        <option value="sub">Subtract (-)</option>
                        <option value="mul">Multiply (*)</option>
                        <option value="div">Divide (/)</option>
                    </select>
                </div>

                <div className="input-group">
                    <label>Value B:</label>
                    <input
                        type="number"
                        value={b}
                        onChange={(e) => setB(e.target.value)}
                    />
                </div>

                <button
                    className="execute-btn"
                    onClick={executeCalculation}
                    disabled={loading}
                >
                    {loading ? 'Calculating...' : 'Execute Algorithm'}
                </button>
            </div>

            {result && (
                <div className={`result-display ${result.status}`}>
                    <h3>Result</h3>
                    {result.status === 'success' ? (
                        <div className="success-data">
                            <span className="value">{result.data.result}</span>
                            <details>
                                <summary>Meta Data</summary>
                                <pre>{JSON.stringify(result.meta, null, 2)}</pre>
                            </details>
                        </div>
                    ) : (
                        <div className="error-data">
                            Error: {result.error || result.meta?.error || 'Unknown error'}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default Calculator;
