import React, { useState, useMemo, useEffect } from 'react';
import { AlertTriangle, AlertCircle, MessageSquare, UserCheck, Check, ArrowUp, ArrowDown, Filter } from 'lucide-react';
import type { Appointment } from '@/types';

interface AbsenteeismAlertsProps {
  appointments: Appointment[];
  triggeredActions: Record<number, string>;
  handleAction: (appId: number, clientHash: string, actionType: 'whatsapp' | 'confirm') => void;
  selectedAppId?: number | null;
}

export const AbsenteeismAlerts: React.FC<AbsenteeismAlertsProps> = ({
  appointments,
  triggeredActions,
  handleAction,
  selectedAppId
}) => {
  const [activeRisks, setActiveRisks] = useState<string[]>(['ALTO', 'MEDIO']);
  
  const [sortField, setSortField] = useState<'risk' | 'time'>('risk');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const toggleRiskFilter = (riskLevel: string) => {
    if (activeRisks.includes(riskLevel)) {
      if (activeRisks.length > 1) {
        setActiveRisks(activeRisks.filter(r => r !== riskLevel));
      }
    } else {
      setActiveRisks([...activeRisks, riskLevel]);
    }
  };

  const toggleSortDirection = () => {
    setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  const processedAlerts = useMemo(() => {
    let list = appointments.filter(app => activeRisks.includes(app.ausentismo_risk));

    list = [...list].sort((a, b) => {
      if (sortField === 'risk') {
        const weight: Record<string, number> = { ALTO: 3, MEDIO: 2, BAJO: 1 };
        const wA = weight[a.ausentismo_risk] || 0;
        const wB = weight[b.ausentismo_risk] || 0;
        if (wA !== wB) {
          return sortDirection === 'desc' ? wB - wA : wA - wB;
        }
        return a.start_time.localeCompare(b.start_time);
      } else {
        const cmp = a.start_time.localeCompare(b.start_time);
        return sortDirection === 'asc' ? cmp : -cmp;
      }
    });

    return list;
  }, [appointments, activeRisks, sortField, sortDirection]);

  useEffect(() => {
    if (selectedAppId) {
      const el = document.getElementById(`alert-card-${selectedAppId}`);
      if (el) {
        el.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [selectedAppId]);

  const getDiagnosisText = (app: Appointment) => {
    if (app.diagnostic) {
      return app.diagnostic;
    }
    const isInactive = app.barber_name.toLowerCase().includes("inactivo");
    if (isInactive) {
      return "El profesional asignado figura inactivo en el sistema.";
    }
    if (app.ausentismo_risk === "ALTO") {
      return "Turno agendado con varios días de anticipación sin confirmar.";
    }
    if (app.ausentismo_risk === "MEDIO") {
      return "Turno en horario concurrido pendiente de reconfirmación.";
    }
    return "Cliente habitual con asistencia regular.";
  };
  return (
    <section className="grid-column">
      <div className="column-card">
        <h2 className="column-title" style={{ borderBottomColor: 'var(--danger-border)', justifyContent: 'center' }}>
          <AlertTriangle size={20} style={{ color: 'var(--danger)' }} />
          Triggers de Ausentismo
        </h2>

        {/* Filter Multi-Select & Sort Control Bar */}
        <div className="triggers-control-bar">
          
          {/* Risk Filter with Label */}
          <div className="filter-step-group">
            <span className="control-label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
              <Filter size={12} /> Filtrar:
            </span>
            <div className="risk-toggle-group">
              <button 
                className={`risk-toggle-btn alto ${activeRisks.includes('ALTO') ? 'active' : ''}`}
                onClick={() => toggleRiskFilter('ALTO')}
              >
                Alto
              </button>
              <button 
                className={`risk-toggle-btn medio ${activeRisks.includes('MEDIO') ? 'active' : ''}`}
                onClick={() => toggleRiskFilter('MEDIO')}
              >
                Medio
              </button>
              <button 
                className={`risk-toggle-btn bajo ${activeRisks.includes('BAJO') ? 'active' : ''}`}
                onClick={() => toggleRiskFilter('BAJO')}
              >
                Bajo
              </button>
            </div>
          </div>

          {/* Sort Control with Label and Interactive ASC/DESC Button */}
          <div className="sort-step-group">
            <span className="control-label">Ordenar por:</span>
            
            <select 
              className="sort-select"
              value={sortField}
              onChange={(e) => setSortField(e.target.value as 'risk' | 'time')}
            >
              <option value="risk">Riesgo</option>
              <option value="time">Horario</option>
            </select>

            {/* Direction Toggle Button (Icon only to save horizontal space) */}
            <button 
              className="sort-dir-btn"
              onClick={toggleSortDirection}
              title={`Orden actual: ${sortDirection === 'asc' ? 'Ascendente (clic para Cambiar a Descendente)' : 'Descendente (clic para Cambiar a Ascendente)'}`}
            >
              {sortDirection === 'asc' ? <ArrowUp size={14} /> : <ArrowDown size={14} />}
            </button>
          </div>

        </div>

        {/* Alerts List */}
        <div className="alerts-list">
          {processedAlerts.length > 0 ? (
            processedAlerts.map((app) => {
              const isTriggered = triggeredActions[app.id] !== undefined;
              const actionType = triggeredActions[app.id];
              const isHigh = app.ausentismo_risk === "ALTO";
              const isSelected = selectedAppId === app.id;

              return (
                <div 
                  key={app.id} 
                  id={`alert-card-${app.id}`}
                  className={`alert-item ${app.ausentismo_risk.toLowerCase()} ${isSelected ? 'focused-alert' : ''}`}
                >
                  
                  <div className="alert-item-header">
                    <span className="alert-client-hash">
                      Turno #{app.id} • Cliente: {app.client_hashed}
                    </span>
                    <span className={`risk-badge ${app.ausentismo_risk.toLowerCase()}`} style={{ fontSize: '0.65rem', padding: '2px 6px' }}>
                      {app.ausentismo_risk}
                    </span>
                  </div>

                  <div className="alert-reason">
                    <AlertCircle size={14} style={{ 
                      color: isHigh ? 'var(--danger)' : app.ausentismo_risk === 'MEDIO' ? 'var(--warning)' : 'var(--success)', 
                      marginTop: '2px', 
                      flexShrink: 0 
                    }} />
                    <span>
                      {getDiagnosisText(app)}
                    </span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                    <span>Hora: {app.start_time.substring(0, 5)} hs</span>
                    <span>Servicio: {app.service_name}</span>
                  </div>

                  <div className="alert-actions">
                    {isTriggered ? (
                      <button className="action-trigger-btn triggered" disabled>
                        <Check size={14} />
                        {actionType === 'whatsapp' ? 'WhatsApp Enviado' : 'Turno Confirmado'}
                      </button>
                    ) : (
                      <>
                        <button 
                          className="action-trigger-btn"
                          onClick={() => handleAction(app.id, app.client_hashed, 'whatsapp')}
                        >
                          <MessageSquare size={14} />
                          Recordatorio
                        </button>
                        <button 
                          className="action-trigger-btn secondary"
                          onClick={() => handleAction(app.id, app.client_hashed, 'confirm')}
                        >
                          <UserCheck size={14} />
                          Confirmar
                        </button>
                      </>
                    )}
                  </div>

                </div>
              );
            })
          ) : (
            <div className="no-alerts-msg">
              <UserCheck size={32} style={{ color: 'var(--success)', opacity: 0.7 }} />
              <span>Sin alertas registradas para las opciones de filtro seleccionadas.</span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
