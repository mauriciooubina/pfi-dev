export interface QueueMetrics {
  utilization: number;
  p0: number;
  Lq: number;
  Wq_hours: number;
  Wq_minutes: number;
  L: number;
  W_hours: number;
  W_minutes: number;
  stable: boolean;
}

export interface ShopQueueData {
  shop_id: string;
  lambda_rate: number;
  mu_rate: number;
  servers: number;
  metrics: QueueMetrics;
}

export interface Appointment {
  id: number;
  barber_id: number;
  barber_name: string;
  date: string;
  start_time: string;
  end_time: string;
  service_name: string;
  service_price: number;
  service_duration: number;
  client_hashed: string;
  is_self_booked: number;
  target: number | null;
  ausentismo_risk: 'ALTO' | 'MEDIO' | 'BAJO' | string;
  color_code: string;
}
