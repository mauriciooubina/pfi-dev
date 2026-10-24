import React from 'react';
import { RefreshCw, Calendar as CalendarIcon, BarChart2, AlertCircle } from 'lucide-react';
import logoImg from '@/assets/logo.jpg';

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
    <header className="app-navbar-unified fade-in">
      
      {/* 1. Left: Brand Identity (Logo Rectangular) */}
      <div className="navbar-brand">
        <img src={logoImg} alt="TurnoFiel" className="navbar-logo-img" />
        {isFallbackMode && (
          <span className="navbar-status-badge fallback" title="Modo degradación local">
            <AlertCircle size={11} /> Fallback
          </span>
        )}
      </div>

      {/* 2. Center: Segmented Navigation Switcher */}
      <nav className="navbar-tabs-segmented">
        <button 
          className={`nav-seg-tab ${activeTab === 'agenda' ? 'active' : ''}`}
          onClick={() => setActiveTab('agenda')}
        >
          <CalendarIcon size={15} />
          <span>Agenda diaria</span>
        </button>
        <button 
          className={`nav-seg-tab ${activeTab === 'queues' ? 'active' : ''}`}
          onClick={() => setActiveTab('queues')}
        >
          <BarChart2 size={15} />
          <span>Análisis de Colas M/M/s</span>
        </button>
      </nav>

      {/* 3. Right: Contextual Controls (Shop Switcher + Date Picker + Refresh) */}
      <div className="navbar-controls">
        
        {/* Shop Switcher */}
        <div className="navbar-control-capsule">
          <select 
            className="navbar-select-input"
            value={shopId} 
            onChange={(e) => setShopId(e.target.value as 'hellfish' | 'hooligans')}
          >
            <option value="hellfish">Hellfish Barbershop</option>
            <option value="hooligans">Barbería Hooligans</option>
          </select>
        </div>

        {/* Date Picker & Refresh Button */}
        <div className="navbar-control-capsule">
          <input 
            type="date" 
            className="navbar-date-input"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
          <button 
            onClick={onRefresh}
            className="navbar-refresh-btn"
            title="Recargar datos"
          >
            <RefreshCw size={13} />
          </button>
        </div>

      </div>

    </header>
  );
};
