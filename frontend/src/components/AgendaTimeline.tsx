import React, { useState, useMemo } from 'react';
import { Calendar as CalendarIcon, Check, Filter, Plus, MessageSquare } from 'lucide-react';
import type { Appointment } from '@/types';

interface AgendaTimelineProps {
  appointments: Appointment[];
  triggeredActions: Record<number, string>;
  selectedAppId?: number | null;
  onSelectApp?: (appId: number) => void;
  onOpenSimulateModal?: () => void;
}

export const AgendaTimeline: React.FC<AgendaTimelineProps> = ({
  appointments,
  triggeredActions,
  selectedAppId,
  onSelectApp,
  onOpenSimulateModal
}) => {
  const [selectedBarber, setSelectedBarber] = useState<string>('ALL');
  const [selectedRisk, setSelectedRisk] = useState<string>('ALL');
  const [selectedChannel, setSelectedChannel] = useState<string>('ALL');

  const uniqueProviders = useMemo(() => {
    return Array.from(new Set(appointments.map(a => a.barber_name)));
  }, [appointments]);

  const filteredAppointments = useMemo(() => {
    return appointments.filter(app => {
      const matchProvider = selectedBarber === 'ALL' || app.barber_name === selectedBarber;
      const matchRisk = selectedRisk === 'ALL' || app.ausentismo_risk === selectedRisk;
      const matchChannel = selectedChannel === 'ALL' ||
        (selectedChannel === 'WEB' && app.is_self_booked === 1) ||
        (selectedChannel === 'MANUAL' && app.is_self_booked === 0);
      return matchProvider && matchRisk && matchChannel;
    });
  }, [appointments, selectedBarber, selectedRisk, selectedChannel]);

  return (
    <section className="grid-column">
      <div className="column-card" style={{ flexGrow: 1 }}>

        {/* Title Header: Botón a la izquierda | Título centrado | Total a la derecha */}
        <div className="column-title" style={{ position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 16px' }}>
          
          {/* Left: Botón Agendar Turno */}
          <div>
            {onOpenSimulateModal && (
              <button 
                className="btn-agendar-turno"
                onClick={onOpenSimulateModal}
                title="Agendar nuevo turno"
              >
                <Plus size={15} />
                Agendar turno
              </button>
            )}
          </div>

          {/* Center: Título Centrado */}
          <div style={{ position: 'absolute', left: '50%', transform: 'translateX(-50%)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CalendarIcon size={18} />
            <span style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Agenda diaria
            </span>
          </div>

          {/* Right: Total de Turnos */}
          <div>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>
              Total: {appointments.length} turnos
            </span>
          </div>

        </div>

        {/* Interactive Filter Controls (Right Aligned underneath) */}
        <div className="agenda-filter-bar" style={{ justifyContent: 'flex-end' }}>
          <div className="filter-group">
            <Filter size={14} style={{ color: 'var(--text-muted)' }} />

            {/* Provider Filter */}
            <select
              className="filter-select"
              value={selectedBarber}
              onChange={(e) => setSelectedBarber(e.target.value)}
            >
              <option value="ALL">Todos los prestadores</option>
              {uniqueProviders.map(p => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>

            {/* Risk Filter */}
            <select
              className="filter-select"
              value={selectedRisk}
              onChange={(e) => setSelectedRisk(e.target.value)}
            >
              <option value="ALL">Todos los riesgos</option>
              <option value="ALTO">Riesgo alto</option>
              <option value="MEDIO">Riesgo medio</option>
              <option value="BAJO">Riesgo bajo</option>
            </select>

            {/* Channel Filter */}
            <select
              className="filter-select"
              value={selectedChannel}
              onChange={(e) => setSelectedChannel(e.target.value)}
            >
              <option value="ALL">Todos los canales</option>
              <option value="WEB">Página web</option>
              <option value="MANUAL">WhatsApp / Manual</option>
            </select>
          </div>

          {(selectedBarber !== 'ALL' || selectedRisk !== 'ALL' || selectedChannel !== 'ALL') && (
            <button
              className="clear-filters-btn"
              onClick={() => {
                setSelectedBarber('ALL');
                setSelectedRisk('ALL');
                setSelectedChannel('ALL');
              }}
            >
              Limpiar filtros
            </button>
          )}
        </div>

        {/* 5-Column Structured Header */}
        <div className="agenda-table-header">
          <span className="col-header time">Horario y duración</span>
          <span className="col-header turn">Turno</span>
          <span className="col-header barber">Prestador</span>
          <span className="col-header channel">Canal de reserva</span>
          <span className="col-header risk">Riesgo</span>
        </div>

        {/* Appointments List */}
        <div className="timeline-list">
          {filteredAppointments.length > 0 ? (
            filteredAppointments.map((app) => {
              const isProviderActive = !app.barber_name.toLowerCase().includes("inactivo");
              const isSelected = selectedAppId === app.id;
              const hasAction = triggeredActions[app.id] !== undefined;
              const actionType = triggeredActions[app.id];

              return (
                <div
                  key={app.id}
                  className={`agenda-row-card ${isSelected ? 'selected' : ''} ${hasAction ? `action-handled ${actionType}` : ''}`}
                  onClick={() => onSelectApp && onSelectApp(app.id)}
                >

                  {/* Col 1: Horario / Duracion */}
                  <div className="col-cell time">
                    <span className="time-start">{app.start_time.substring(0, 5)}</span>
                    <span className="time-duration">{app.service_duration} min</span>
                  </div>

                  {/* Col 2: Turno (ID + Status Chip + Cliente + Servicio + Precio) */}
                  <div className="col-cell turn">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span className="turn-id-tag" style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--secondary)' }}>
                        #{app.id}
                      </span>
                      {hasAction && (
                        <span className={`handled-status-tag ${actionType}`}>
                          {actionType === 'whatsapp' ? (
                            <>
                              <MessageSquare size={10} /> Notificado
                            </>
                          ) : (
                            <>
                              <Check size={11} /> Confirmado
                            </>
                          )}
                        </span>
                      )}
                    </div>
                    <div className="client-title" style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      <span>Cliente {app.client_hashed}</span>
                    </div>
                    <div className="service-sub">
                      <span>{app.service_name}</span>
                    </div>
                    <div className="service-sub">
                      <span className="price-tag">${app.service_price.toLocaleString('es-AR')}</span>
                    </div>
                  </div>

                  {/* Col 3: Prestador (Professional) */}
                  <div className="col-cell barber">
                    <span className={`barber-badge ${isProviderActive ? '' : 'inactive'}`}>
                      {app.barber_name} {!isProviderActive && '(Inactivo)'}
                    </span>
                  </div>

                  {/* Col 4: Canal de Reserva */}
                  <div className="col-cell channel">
                    <span className={`channel-badge ${app.is_self_booked === 1 ? 'web' : 'manual'}`}>
                      {app.is_self_booked === 1 ? 'Página web' : 'WhatsApp / Manual'}
                    </span>
                  </div>

                  {/* Col 5: Riesgo Predicho por ML */}
                  <div className="col-cell risk">
                    <span className={`risk-badge ${app.ausentismo_risk.toLowerCase()}`}>
                      {app.ausentismo_risk}
                    </span>
                  </div>

                </div>
              );
            })
          ) : (
            <div style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '60px 0' }}>
              No hay turnos registrados que coincidan con los filtros seleccionados.
            </div>
          )}
        </div>
      </div>
    </section>
  );
};
