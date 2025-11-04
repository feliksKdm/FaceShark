import React, { useState } from 'react';
import axios from 'axios';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
      setResult(null);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/analyze', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка при анализе изображения');
    } finally {
      setLoading(false);
    }
  };

  const getLabelColor = (label) => {
    switch (label) {
      case 'mogged':
        return '#10b981'; // green
      case 'sigma':
        return '#3b82f6'; // blue
      case 'meh':
        return '#f59e0b'; // amber
      default:
        return '#6b7280'; // gray
    }
  };

  const getLabelText = (label) => {
    switch (label) {
      case 'mogged':
        return 'MOGGED';
      case 'sigma':
        return 'SIGMA';
      case 'meh':
        return 'MEH';
      default:
        return label.toUpperCase();
    }
  };

  const radarData = result?.axes ? [
    { axis: 'Резкость', value: result.axes.sharpness },
    { axis: 'Освещение', value: result.axes.lighting },
    { axis: 'Поза', value: result.axes.pose },
    { axis: 'Челюсть', value: result.axes.jawline },
    { axis: 'Контраст', value: result.axes.contrast },
  ] : [];

  return (
    <div className="app">
      <header className="header">
        <h1>🎯 FaceSharp</h1>
        <p>Оценка качества селфи с мем-лейблами</p>
      </header>

      <main className="main">
        <div className="upload-section">
          <div className="upload-box">
            <input
              type="file"
              id="file-input"
              accept="image/*"
              onChange={handleFileChange}
              style={{ display: 'none' }}
            />
            <label htmlFor="file-input" className="upload-button">
              {preview ? 'Изменить фото' : 'Выбрать фото'}
            </label>

            {preview && (
              <div className="preview-container">
                <img src={preview} alt="Preview" className="preview-image" />
                <button
                  onClick={handleAnalyze}
                  disabled={loading}
                  className="analyze-button"
                >
                  {loading ? 'Анализ...' : 'Анализировать'}
                </button>
              </div>
            )}
          </div>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {result && result.ok && (
          <div className="results-section">
            <div className="result-card">
              <div className="result-header">
                <div
                  className="label-badge"
                  style={{ backgroundColor: getLabelColor(result.label) }}
                >
                  {getLabelText(result.label)}
                </div>
                <div className="confidence">
                  Уверенность: {(result.confidence * 100).toFixed(0)}%
                </div>
              </div>

              <div className="radar-chart-container">
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="axis" />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar
                      name="Оси"
                      dataKey="value"
                      stroke={getLabelColor(result.label)}
                      fill={getLabelColor(result.label)}
                      fillOpacity={0.6}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              <div className="axes-grid">
                {Object.entries(result.axes).map(([key, value]) => (
                  <div key={key} className="axis-item">
                    <div className="axis-label">
                      {key === 'sharpness' && 'Резкость'}
                      {key === 'lighting' && 'Освещение'}
                      {key === 'pose' && 'Поза'}
                      {key === 'jawline' && 'Челюсть'}
                      {key === 'contrast' && 'Контраст'}
                    </div>
                    <div className="axis-bar">
                      <div
                        className="axis-fill"
                        style={{
                          width: `${value}%`,
                          backgroundColor: getLabelColor(result.label)
                        }}
                      />
                    </div>
                    <div className="axis-value">{value.toFixed(0)}</div>
                  </div>
                ))}
              </div>

              {result.reasons && result.reasons.length > 0 && (
                <div className="reasons-section">
                  <h3>Причины оценки:</h3>
                  <ul className="reasons-list">
                    {result.reasons.map((reason, index) => (
                      <li key={index}>{reason}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.pose && (
                <div className="pose-info">
                  <h3>Поза:</h3>
                  <div className="pose-details">
                    <span>Yaw: {result.pose.yaw.toFixed(1)}°</span>
                    <span>Pitch: {result.pose.pitch.toFixed(1)}°</span>
                    <span>Roll: {result.pose.roll.toFixed(1)}°</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {result && result.abstain && (
          <div className="abstain-message">
            Недостаточно данных для точной оценки. Попробуйте другое фото.
          </div>
        )}
      </main>
    </div>
  );
}

export default App;

