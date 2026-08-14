import React from 'react';
import { RefreshCw, Calendar as CalendarIcon, BarChart2, AlertCircle } from 'lucide-react';

interface HeaderProps {
  shopId: 'hellfish' | 'hooligans';
  setShopId: (shop: 'hellfish' | 'hooligans') => void;
  date: string;
  setDate: (date: string) => void;
  isFallbackMode: boolean;
  onRefresh: () => void;
  activeTab: 'agenda' | 'queues';
  setActiveTab: (tab: 'agenda' | 'queues') => void;
}

export const Header: React.FC<HeaderProps> = ({
  shopId,
  setShopId,
  date,
  setDate,
  isFallbackMode,
  onRefresh,
  activeTab,
  setActiveTab
}) => {
  return (
    <header className="app-header fade-in">
      
      {/* Title Hero */}
      <div className="header-title-area">
        <h1>SISTEMA DE PREDICCIÓN DE AUSENTISMO</h1>
        <p>
          PFI UADE 2026 — Agenda Híbrida y Modelado Estocástico M/M/s
          {isFallbackMode && (
            <span style={{ 
              marginLeft: '12px', 
              color: 'var(--warning)', 
              fontSize: '0.8rem', 
              background: 'var(--warning-bg)',
              border: '1px solid var(--warning-border)',
              padding: '2px 8px', 
              borderRadius: '6px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              <AlertCircle size={12} /> MODALIDAD LOCAL DEMO
            </span>
          )}
        </p>
      </div>

      {/* Step-by-Step Selector Bar */}
      <div className="hero-selector-bar">
        
        {/* Step 1: Shop Selection */}
        <div className="selector-step">
          <span className="step-label">Seleccioná el Local:</span>
          <div className="shop-selector">
            <button 
              className={`shop-btn ${shopId === 'hellfish' ? 'active' : ''}`}
              onClick={() => setShopId('hellfish')}
            >
              Hellfish Barbershop
            </button>
            <button 
              className={`shop-btn ${shopId === 'hooligans' ? 'active' : ''}`}
              onClick={() => setShopId('hooligans')}
            >
              Barbería Hooligans
            </button>
          </div>
        </div>

        {/* Step 2: Date Selection & Refresh */}
        <div className="selector-step">
          <span className="step-label">Seleccioná la Fecha:</span>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <input 
              type="date" 
              className="date-selector"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />

            <button 
              onClick={onRefresh}
              className="refresh-btn"
              title="Recargar Datos"
            >
              <RefreshCw size={16} />
            </button>
          </div>
        </div>

      </div>

      {/* Main Navigation Tabs */}
      <nav className="header-tabs">
        <button 
          className={`tab-btn ${activeTab === 'agenda' ? 'active' : ''}`}
          onClick={() => setActiveTab('agenda')}
        >
          <CalendarIcon size={16} />
          Agenda & Alertas de Ausentismo
        </button>
        <button 
          className={`tab-btn ${activeTab === 'queues' ? 'active' : ''}`}
          onClick={() => setActiveTab('queues')}
        >
          <BarChart2 size={16} />
          Análisis de Colas M/M/s
        </button>
      </nav>

    </header>
  );
};
