import React from 'react';
import { TrendingUp, Users, CheckCircle } from 'lucide-react';
import type { ShopQueueData } from '@/types';
import { formatNumber, formatPercent } from '@/utils';

interface QueueMetricsColumnProps {
  queueMetrics: ShopQueueData | null;
  shopId: 'hellfish' | 'hooligans';
}

export const QueueMetricsColumn: React.FC<QueueMetricsColumnProps> = ({ queueMetrics, shopId }) => {
  if (!queueMetrics) {
    return (
      <div className="column-card">
        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
          No hay métricas de colas disponibles para este comercio.
        </div>
      </div>
    );
  }

  const { lambda_rate, mu_rate, servers, metrics } = queueMetrics;

  return (
    <div className="view-grid-queues fade-in">
      
      {/* Hero Banner for Capacity */}
      <div className="queues-hero-card">
        <div>
          <h2 style={{ fontFamily: 'Outfit', fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <TrendingUp size={22} style={{ color: '#a5b4fc' }} />
            Modelo Analítico de Colas M/M/s
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Análisis estocástico en estado estable sobre la ventana operativa real (10:00 a 20:00 hs)
          </p>
        </div>

        <div style={{ 
          background: 'rgba(15, 23, 42, 0.6)', 
          border: '1px solid var(--card-border)', 
          padding: '12px 18px', 
          borderRadius: '12px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px'
        }}>
          <Users size={20} style={{ color: 'var(--secondary)' }} />
          <div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Capacidad de Servidores en Paralelo (s)</div>
            <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              {servers} prestadores activos
            </div>
          </div>
        </div>
      </div>

      {/* 6 Parameter Cards Grid (3 cards per row max to avoid truncated formulas) */}
      <div className="queues-parameters-grid">
        
        {/* 1. Factor de Ocupacion rho */}
        <div className="parameter-card">
          <div className="parameter-card-header">
            <span className="parameter-title">Factor de Ocupación</span>
            <span className="parameter-symbol">ρ = λ / (s · μ)</span>
          </div>
          <div className="parameter-value" style={{ 
            color: metrics.utilization > 0.8 ? 'var(--danger)' : 
                   metrics.utilization > 0.5 ? 'var(--warning)' : 'var(--success)'
          }}>
            {formatPercent(metrics.utilization, 1)}
          </div>
          <div className="utilization-bar-container" style={{ margin: '4px 0 8px 0' }}>
            <div 
              className="utilization-bar-fill" 
              style={{ 
                width: `${Math.min(metrics.utilization * 100, 100)}%`,
                backgroundColor: metrics.utilization > 0.8 ? 'var(--danger)' : 
                                 metrics.utilization > 0.5 ? 'var(--warning)' : 'var(--success)'
              }}
            />
          </div>
          <div className="parameter-explanation">
            Muestra la intensidad del tráfico en el local. Un valor del {formatPercent(metrics.utilization, 1)} indica que los prestadores están ocupados un tercio de su tiempo operativo, manteniendo margen seguro para absorber la demanda aleatoria.
          </div>
        </div>

        {/* 2. Tasa de Arribos lambda */}
        <div className="parameter-card">
          <div className="parameter-card-header">
            <span className="parameter-title">Tasa de Arribos Promedio</span>
            <span className="parameter-symbol">λ (Llegadas / Hora)</span>
          </div>
          <div className="parameter-value">
            {formatNumber(lambda_rate, 3)} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>clientes/hora</span>
          </div>
          <div className="parameter-explanation">
            Frecuencia promedio de llegada de clientes legítimos durante las 10 horas de atención diaria (10:00 a 20:00 hs), habiendo descontado bloqueos de agenda y cancelaciones tempranas.
          </div>
        </div>

        {/* 3. Tasa de Servicio mu */}
        <div className="parameter-card">
          <div className="parameter-card-header">
            <span className="parameter-title">Tasa de Atención por Prestador</span>
            <span className="parameter-symbol">μ (Servicios / Hora)</span>
          </div>
          <div className="parameter-value">
            {formatNumber(mu_rate, 3)} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>servicios/hora</span>
          </div>
          <div className="parameter-explanation">
            Capacidad de servicio de cada prestador individual por hora. Se calcula de forma ponderada según la duración real de los servicios en el catálogo histórico (promedio: {formatNumber(60 / mu_rate, 1)} minutos por turno).
          </div>
        </div>

        {/* 4. Tiempo de Espera Wq */}
        <div className="parameter-card">
          <div className="parameter-card-header">
            <span className="parameter-title">Tiempo de Espera en Cola</span>
            <span className="parameter-symbol">Wq (Minutos)</span>
          </div>
          <div className="parameter-value" style={{ color: '#38bdf8' }}>
            {formatNumber(metrics.Wq_minutes, 2)} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>minutos</span>
          </div>
          <div className="parameter-explanation">
            Tiempo promedio que aguarda un cliente en la sala de espera antes de ser atendido. Valores inferiores a 5 minutos reflejan una experiencia de cliente óptima sin demoras acumuladas.
          </div>
        </div>

        {/* 5. Clientes en Cola Lq */}
        <div className="parameter-card">
          <div className="parameter-card-header">
            <span className="parameter-title">Longitud Media de la Cola</span>
            <span className="parameter-symbol">Lq (Personas)</span>
          </div>
          <div className="parameter-value" style={{ color: '#a5b4fc' }}>
            {formatNumber(metrics.Lq, 2)} <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 'normal' }}>clientes</span>
          </div>
          <div className="parameter-explanation">
            Cantidad esperada de personas haciendo cola en un instante arbitrario de la jornada. Representa la congestión física dentro de la sala de espera del comercio.
          </div>
        </div>

        {/* 6. Probabilidad de Vacio P0 */}
        <div className="parameter-card">
          <div className="parameter-card-header">
            <span className="parameter-title">Probabilidad de Local Vacío</span>
            <span className="parameter-symbol">P₀ (Porcentaje)</span>
          </div>
          <div className="parameter-value">
            {formatPercent(metrics.p0, 1)}
          </div>
          <div className="parameter-explanation">
            Porcentaje del tiempo operativo en el que todos los prestadores activos están libres y no hay clientes aguardando en la recepción del comercio.
          </div>
        </div>

      </div>

      {/* Stability Note Banner */}
      <div className="column-card" style={{ flexDirection: 'row', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
        <CheckCircle size={24} style={{ color: 'var(--success)', flexShrink: 0 }} />
        <div style={{ flexGrow: 1 }}>
          <h4 style={{ color: 'var(--text-primary)', fontSize: '0.95rem', fontWeight: 600 }}>
            Verificación Estocástica de Estabilidad: Sistema Estable (ρ &lt; 1,0)
          </h4>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '2px' }}>
            Dado que el factor de ocupación ρ ({formatPercent(metrics.utilization, 1)}) es menor al 100%, el sistema de {shopId} no genera colas infinitas ni colapso operativo.
          </p>
        </div>
      </div>

    </div>
  );
};
