import type { ShopQueueData, Appointment } from '@/types';

export const FALLBACK_QUEUES: ShopQueueData[] = [
  {
    shop_id: "hellfish",
    lambda_rate: 1.5372,
    mu_rate: 1.6369,
    servers: 3,
    metrics: {
      utilization: 0.3130,
      p0: 0.3875,
      Lq: 0.0355,
      Wq_hours: 0.0231,
      Wq_minutes: 1.3845,
      L: 0.9745,
      W_hours: 0.6340,
      W_minutes: 38.0390,
      stable: true
    }
  },
  {
    shop_id: "hooligans",
    lambda_rate: 0.9605,
    mu_rate: 1.8458,
    servers: 2,
    metrics: {
      utilization: 0.2602,
      p0: 0.5871,
      Lq: 0.0378,
      Wq_hours: 0.0393,
      Wq_minutes: 2.3606,
      L: 0.5582,
      W_hours: 0.5811,
      W_minutes: 34.8673,
      stable: true
    }
  }
];

export const FALLBACK_CALENDAR: Record<string, Appointment[]> = {
  hellfish: [
    { id: 146, barber_id: 2, barber_name: "Martín", date: "2026-03-03", start_time: "11:00:00", end_time: "11:45:00", service_name: "Corte y Barba", service_price: 6000.0, service_duration: 45, client_hashed: "9ca60626b6b70dfb", is_self_booked: 1, target: 1, ausentismo_risk: "BAJO", color_code: "#10b981" },
    { id: 1, barber_id: 2, barber_name: "Martín", date: "2026-03-03", start_time: "12:00:00", end_time: "12:20:00", service_name: "Perfilado de Barba", service_price: 2500.0, service_duration: 20, client_hashed: "4f2913b10c26749c", is_self_booked: 1, target: 0, ausentismo_risk: "BAJO", color_code: "#10b981" },
    { id: 61, barber_id: 3, barber_name: "Alan", date: "2026-03-03", start_time: "12:30:00", end_time: "14:00:00", service_name: "Color y Fade", service_price: 12000.0, service_duration: 90, client_hashed: "bc0064e4daf309c2", is_self_booked: 1, target: 0, ausentismo_risk: "ALTO", color_code: "#f43f5e" },
    { id: 386, barber_id: 1, barber_name: "Facundo", date: "2026-03-03", start_time: "13:00:00", end_time: "13:30:00", service_name: "Corte Clásico", service_price: 4500.0, service_duration: 30, client_hashed: "bc0064e4daf309c2", is_self_booked: 1, target: 0, ausentismo_risk: "BAJO", color_code: "#10b981" },
    { id: 56, barber_id: 3, barber_name: "Alan", date: "2026-03-03", start_time: "13:30:00", end_time: "15:00:00", service_name: "Color y Fade", service_price: 12000.0, service_duration: 90, client_hashed: "d20b4d0cb9ef72d7", is_self_booked: 1, target: 0, ausentismo_risk: "ALTO", color_code: "#f43f5e" },
    { id: 473, barber_id: 6, barber_name: "Mauro", date: "2026-03-03", start_time: "14:00:00", end_time: "14:45:00", service_name: "Corte y Barba", service_price: 6000.0, service_duration: 45, client_hashed: "d20b4d0cb9ef72d7", is_self_booked: 1, target: 0, ausentismo_risk: "BAJO", color_code: "#10b981" },
    { id: 10, barber_id: 5, barber_name: "Mauro (Inactivo)", date: "2026-03-03", start_time: "14:30:00", end_time: "15:00:00", service_name: "Corte Clásico", service_price: 4500.0, service_duration: 30, client_hashed: "4f2913b10c26749c", is_self_booked: 1, target: 0, ausentismo_risk: "ALTO", color_code: "#f43f5e" },
    { id: 300, barber_id: 1, barber_name: "Facundo", date: "2026-03-03", start_time: "16:00:00", end_time: "16:30:00", service_name: "Corte Clásico", service_price: 4500.0, service_duration: 30, client_hashed: "bc0064e4daf309c2", is_self_booked: 1, target: 1, ausentismo_risk: "ALTO", color_code: "#f43f5e" },
    { id: 1322, barber_id: 5, barber_name: "Mauro (Inactivo)", date: "2026-03-03", start_time: "17:00:00", end_time: "17:45:00", service_name: "Corte y Barba", service_price: 6000.0, service_duration: 45, client_hashed: "4f2913b10c26749c", is_self_booked: 1, target: 0, ausentismo_risk: "ALTO", color_code: "#f43f5e" },
    { id: 270, barber_id: 2, barber_name: "Martín", date: "2026-03-03", start_time: "17:30:00", end_time: "18:15:00", service_name: "Corte y Barba", service_price: 6000.0, service_duration: 45, client_hashed: "c346277baa83c0f6", is_self_booked: 1, target: 0, ausentismo_risk: "MEDIO", color_code: "#f59e0b" },
  ],
  hooligans: [
    { id: 2, barber_id: 5, barber_name: "Valentino", date: "2026-03-03", start_time: "10:30:00", end_time: "11:00:00", service_name: "Corte Clásico", service_price: 4500.0, service_duration: 30, client_hashed: "8bc3921bf3a2cd54", is_self_booked: 0, target: 0, ausentismo_risk: "BAJO", color_code: "#10b981" },
    { id: 15, barber_id: 4, barber_name: "Valen (Inactivo)", date: "2026-03-03", start_time: "11:00:00", end_time: "11:45:00", service_name: "Corte y Barba", service_price: 6000.0, service_duration: 45, client_hashed: "2ba510ee4fb4a2cc", is_self_booked: 1, target: 1, ausentismo_risk: "ALTO", color_code: "#f43f5e" },
    { id: 24, barber_id: 1, barber_name: "Sebastián Fraga", date: "2026-03-03", start_time: "12:00:00", end_time: "12:30:00", service_name: "Corte Clásico", service_price: 4500.0, service_duration: 30, client_hashed: "ab23ccb77e31b234", is_self_booked: 1, target: 0, ausentismo_risk: "BAJO", color_code: "#10b981" },
    { id: 48, barber_id: 5, barber_name: "Valentino", date: "2026-03-03", start_time: "13:30:00", end_time: "15:00:00", service_name: "Color y Fade", service_price: 12000.0, service_duration: 90, client_hashed: "1b234bb4be2fc3ef", is_self_booked: 1, target: 1, ausentismo_risk: "ALTO", color_code: "#f43f5e" },
    { id: 99, barber_id: 1, barber_name: "Sebastián Fraga", date: "2026-03-03", start_time: "15:00:00", end_time: "15:20:00", service_name: "Perfilado de Barba", service_price: 2500.0, service_duration: 20, client_hashed: "f8b3c8f3e2ba09c5", is_self_booked: 1, target: 0, ausentismo_risk: "MEDIO", color_code: "#f59e0b" },
  ]
};
