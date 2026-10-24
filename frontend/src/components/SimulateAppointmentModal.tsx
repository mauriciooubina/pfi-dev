import React, { useState, useEffect, useMemo } from 'react';
import { X, Plus, CalendarPlus, UserCheck, UserPlus, AlertTriangle, Users } from 'lucide-react';
import type { Appointment } from '@/types';

interface SimulateAppointmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  shopId: 'hellfish' | 'hooligans';
  currentDate: string;
  onAppointmentCreated: (appointment: Appointment) => void;
}

type ClientProfileKey = 'franco' | 'matias' | 'tomas' | 'gonzalo';

interface ClientProfileData {
  id: ClientProfileKey;
  name: string;
  category: string;
  stats: string;
  description: string;
  themeClass: string;
}

const CLIENT_PROFILES: ClientProfileData[] = [
  {
    id: 'franco',
    name: 'Franco Martínez',
    category: 'Cliente Habitual',
    stats: '12 asistencias / 0 faltas (0% ausentismo)',
    description: 'Historial impecable. Riesgo esperado: BAJO',
    themeClass: 'fiel'
  },
  {
    id: 'matias',
    name: 'Matías Giménez',
    category: 'Cliente Ocasional',
    stats: '4 turnos / 2 faltas (50% ausentismo)',
    description: 'Sensible a antelación: BAJO (24h) / MEDIO (sobre la hora)',
    themeClass: 'ocasional'
  },
  {
    id: 'tomas',
    name: 'Tomás Rodríguez',
    category: 'Cliente Nuevo',
    stats: '0 turnos previos (sin historial)',
    description: 'Primer turno en el local. Riesgo moderado',
    themeClass: 'nuevo'
  },
  {
    id: 'gonzalo',
    name: 'Gonzalo Castro',
    category: 'Cliente Reincidente',
    stats: '4 turnos / 3 faltas (75% ausentismo)',
    description: 'Alto ausentismo recurrente. Riesgo esperado: ALTO',
    themeClass: 'riesgo'
  }
];

const SHOP_BARBERS: Record<'hellfish' | 'hooligans', { id: number; name: string }[]> = {
  hellfish: [
    { id: 1, name: 'Facundo (Yayu)' },
    { id: 2, name: 'Martin' },
    { id: 6, name: 'Mauro' }
  ],
  hooligans: [
    { id: 1, name: 'Sebastian Fraga' },
    { id: 5, name: 'Valentino' }
  ]
};

const SHOP_SERVICES: Record<'hellfish' | 'hooligans', { name: string; price: number; duration: number }[]> = {
  hellfish: [
    { name: 'Corte', price: 22000, duration: 30 },
    { name: 'Afeitado a vapor', price: 15000, duration: 30 },
    { name: 'Corte + Arreglo de Barba', price: 27000, duration: 60 },
    { name: 'Corte para niños', price: 22000, duration: 30 },
    { name: 'Perfilado de cejas', price: 0, duration: 30 }
  ],
  hooligans: [
    { name: 'Corte de Pelo', price: 18000, duration: 30 },
    { name: 'Arreglo de Barba', price: 13000, duration: 30 },
    { name: 'Corte + Barba', price: 23000, duration: 45 },
    { name: 'Corte SOCIOS C.A.P', price: 15500, duration: 30 },
    { name: 'Corte + Barba SOCIOS C.A.P', price: 19500, duration: 30 }
  ]
};

export const SimulateAppointmentModal: React.FC<SimulateAppointmentModalProps> = ({
  isOpen,
  onClose,
  shopId,
  currentDate,
  onAppointmentCreated
}) => {
  const [profile, setProfile] = useState<ClientProfileKey>('matias');

  const barbers = useMemo(() => SHOP_BARBERS[shopId] || [], [shopId]);
  const services = useMemo(() => SHOP_SERVICES[shopId] || [], [shopId]);

  const [barberId, setBarberId] = useState<number>(barbers[0]?.id || 1);
  const [barberName, setBarberName] = useState<string>(barbers[0]?.name || '');

  const [serviceName, setServiceName] = useState<string>(services[0]?.name || '');
  const [servicePrice, setServicePrice] = useState<number>(services[0]?.price || 18000);
  const [serviceDuration, setServiceDuration] = useState<number>(services[0]?.duration || 30);

  const [appointmentDate, setAppointmentDate] = useState<string>(currentDate);
  const [appointmentTime, setAppointmentTime] = useState<string>('16:00');
  const [bookingChannel, setBookingChannel] = useState<'WEB' | 'MANUAL'>('WEB');

  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Sync state whenever shopId or currentDate changes
  useEffect(() => {
    const defaultBarber = SHOP_BARBERS[shopId]?.[0] || { id: 1, name: 'Profesional' };
    setBarberId(defaultBarber.id);
    setBarberName(defaultBarber.name);

    const defaultService = SHOP_SERVICES[shopId]?.[0] || { name: 'Corte', price: 18000, duration: 30 };
    setServiceName(defaultService.name);
    setServicePrice(defaultService.price);
    setServiceDuration(defaultService.duration);

    setAppointmentDate(currentDate);
  }, [shopId, currentDate]);

  // Handle service dropdown change with auto-fill
  const handleServiceChange = (name: string) => {
    setServiceName(name);
    const selected = services.find((s) => s.name === name);
    if (selected) {
      setServicePrice(selected.price);
      setServiceDuration(selected.duration);
    }
  };

  // Handle barber change
  const handleBarberChange = (id: number) => {
    setBarberId(id);
    const b = barbers.find((barber) => barber.id === id);
    if (b) {
      setBarberName(b.name);
    }
  };

  // Calculate live lead time against now()
  const leadTimeInfo = useMemo(() => {
    try {
      const cleanTime = appointmentTime.length === 5 ? `${appointmentTime}:00` : appointmentTime;
      const target = new Date(`${appointmentDate}T${cleanTime}`);
      const now = new Date();
      const diffMs = target.getTime() - now.getTime();
      const hours = diffMs / (1000 * 60 * 60);

      if (isNaN(hours)) {
        return { hours: 24, label: '24 horas' };
      }

      if (hours <= 0) {
        return { hours: 1, label: 'Sobre la hora (< 1 hora de antelación)' };
      }

      if (hours < 24) {
        return { hours: Math.round(hours * 10) / 10, label: `${hours.toFixed(1)} horas (mismo día)` };
      }

      const days = Math.round((hours / 24) * 10) / 10;
      return { hours: Math.round(hours * 10) / 10, label: `${days} días (${Math.round(hours)} horas)` };
    } catch {
      return { hours: 24, label: '24 horas' };
    }
  }, [appointmentDate, appointmentTime]);

  if (!isOpen) return null;

  const currentProfileData = CLIENT_PROFILES.find((p) => p.id === profile) || CLIENT_PROFILES[0];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrorMsg(null);

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

    const cleanTime = appointmentTime.length === 5 ? `${appointmentTime}:00` : appointmentTime;

    const payload = {
      shop_id: shopId,
      barber_id: barberId,
      barber_name: barberName,
      service_name: serviceName,
      service_price: servicePrice,
      service_duration: serviceDuration,
      date: appointmentDate,
      start_time: cleanTime,
      lead_time_hours: leadTimeInfo.hours,
      client_profile: profile,
      client_name: currentProfileData.name,
      is_self_booked: bookingChannel === 'WEB' ? 1 : 0
    };

    try {
      const res = await fetch(`${API_URL}/api/calendar/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        throw new Error(`Error en el servidor (${res.status})`);
      }

      const createdApp: Appointment = await res.json();
      onAppointmentCreated(createdApp);
      onClose();
    } catch (err: any) {
      console.warn('Fallo backend live simulation, creando turno en memoria:', err);

      // Fallback local simulation based on profile and lead time
      let mockRisk: 'BAJO' | 'MEDIO' | 'ALTO' = 'BAJO';
      let mockColor = '#10b981';

      if (profile === 'gonzalo') {
        mockRisk = 'ALTO';
        mockColor = '#ef4444';
      } else if (profile === 'matias') {
        if (leadTimeInfo.hours <= 2) {
          mockRisk = 'MEDIO';
          mockColor = '#f59e0b';
        } else {
          mockRisk = 'BAJO';
          mockColor = '#10b981';
        }
      } else if (profile === 'tomas') {
        mockRisk = leadTimeInfo.hours > 48 ? 'MEDIO' : 'BAJO';
        mockColor = mockRisk === 'MEDIO' ? '#f59e0b' : '#10b981';
      }

      const fallbackApp: Appointment = {
        id: Math.floor(9000 + Math.random() * 900),
        barber_id: barberId,
        barber_name: barberName,
        date: appointmentDate,
        start_time: cleanTime.slice(0, 5),
        end_time: '16:45',
        service_name: serviceName,
        service_price: servicePrice,
        service_duration: serviceDuration,
        client_hashed: currentProfileData.name,
        is_self_booked: bookingChannel === 'WEB' ? 1 : 0,
        target: null,
        ausentismo_risk: mockRisk,
        color_code: mockColor,
        diagnostic: `${currentProfileData.name} (${currentProfileData.category}) agendó turno con ${leadTimeInfo.label}.`
      };

      onAppointmentCreated(fallbackApp);
      onClose();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2>
            <CalendarPlus size={20} color="#0f172a" />
            Agendar nuevo turno
          </h2>
          <button className="modal-close-btn" onClick={onClose} title="Cerrar">
            <X size={20} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="modal-body">
          {/* 1. Client Profile Selector */}
          <div className="profile-selector-area">
            <span className="profile-selector-label">1. Perfil del Cliente:</span>
            <div className="profile-pills-row">
              {CLIENT_PROFILES.map((p) => {
                const isActive = profile === p.id;
                return (
                  <button
                    key={p.id}
                    type="button"
                    className={`profile-pill-btn ${isActive ? `active ${p.themeClass}` : ''}`}
                    onClick={() => setProfile(p.id)}
                  >
                    <span className={`pill-title ${p.themeClass}`}>
                      {p.id === 'franco' && <UserCheck size={16} />}
                      {p.id === 'matias' && <Users size={16} />}
                      {p.id === 'tomas' && <UserPlus size={16} />}
                      {p.id === 'gonzalo' && <AlertTriangle size={16} />}
                      {p.name}
                    </span>
                    <span className="pill-stats">{p.category}</span>
                    <span className="pill-desc">{p.stats}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 2. Form Fields */}
          <div className="modal-form-grid">
            {/* Prestador */}
            <div className="form-field">
              <label>Prestador:</label>
              <select
                className="form-input"
                value={barberId}
                onChange={(e) => handleBarberChange(Number(e.target.value))}
              >
                {barbers.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Servicio */}
            <div className="form-field">
              <label>Servicio:</label>
              <select
                className="form-input"
                value={serviceName}
                onChange={(e) => handleServiceChange(e.target.value)}
              >
                {services.map((s) => (
                  <option key={s.name} value={s.name}>
                    {s.name} (${s.price.toLocaleString('es-AR')} - {s.duration}m)
                  </option>
                ))}
              </select>
            </div>

            {/* Fecha del Turno */}
            <div className="form-field">
              <label>Fecha:</label>
              <input
                type="date"
                className="form-input"
                value={appointmentDate}
                onChange={(e) => setAppointmentDate(e.target.value)}
                required
              />
            </div>

            {/* Horario del Turno */}
            <div className="form-field">
              <label>Horario:</label>
              <input
                type="time"
                className="form-input"
                value={appointmentTime}
                onChange={(e) => setAppointmentTime(e.target.value)}
                required
              />
            </div>

            {/* Canal de Reserva */}
            <div className="form-field">
              <label>Canal de reserva:</label>
              <select
                className="filter-select"
                value={bookingChannel}
                onChange={(e) => setBookingChannel(e.target.value as 'WEB' | 'MANUAL')}
              >
                <option value="WEB">Página web</option>
                <option value="MANUAL">WhatsApp / Manual</option>
              </select>
            </div>

            {/* Precio ($) y Duración (min) */}
            <div className="form-field">
              <label>Precio y Duración Estimada:</label>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                <input
                  type="number"
                  className="form-input"
                  value={servicePrice}
                  onChange={(e) => setServicePrice(Number(e.target.value))}
                  step={500}
                  placeholder="Precio $"
                  required
                />
                <input
                  type="number"
                  className="form-input"
                  value={serviceDuration}
                  onChange={(e) => setServiceDuration(Number(e.target.value))}
                  step={5}
                  placeholder="Min"
                  required
                />
              </div>
            </div>
          </div>

          {errorMsg && (
            <div style={{ color: 'var(--danger)', fontSize: '0.85rem' }}>
              {errorMsg}
            </div>
          )}

          {/* Footer Buttons */}
          <div className="modal-footer" style={{ margin: '-24px', marginTop: '0', padding: '16px 24px' }}>
            <button type="button" className="modal-cancel-btn" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="modal-submit-btn" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <span className="spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
                  Procesando turno...
                </>
              ) : (
                <>
                  <Plus size={16} />
                  Confirmar turno
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
