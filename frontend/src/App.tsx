import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { QueueMetricsColumn } from '@/components/QueueMetricsColumn';
import { AgendaTimeline } from '@/components/AgendaTimeline';
import { AbsenteeismAlerts } from '@/components/AbsenteeismAlerts';
import { ToastNotification } from '@/components/ToastNotification';
import { FALLBACK_QUEUES, FALLBACK_CALENDAR } from '@/data/fallbackData';
import type { ShopQueueData, Appointment } from '@/types';
import '@/styles/App.css';

function App() {
  const [shopId, setShopId] = useState<'hellfish' | 'hooligans'>('hellfish');
  const [date, setDate] = useState<string>('2026-03-03');
  const [activeTab, setActiveTab] = useState<'agenda' | 'queues'>('agenda');
  
  const [loading, setLoading] = useState<boolean>(true);
  const [isFallbackMode, setIsFallbackMode] = useState<boolean>(false);
  
  const [queueMetrics, setQueueMetrics] = useState<ShopQueueData | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedAppId, setSelectedAppId] = useState<number | null>(null);
  
  // Interactive action states
  const [triggeredActions, setTriggeredActions] = useState<Record<number, string>>({});
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  // Fetch metrics and calendar from API
  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Fetch queues
      const queuesRes = await fetch(`${API_URL}/api/queues`);
      if (!queuesRes.ok) throw new Error('API Queues error');
      const queuesData: ShopQueueData[] = await queuesRes.json();
      
      const currentShopQueue = queuesData.find((q) => q.shop_id === shopId);
      setQueueMetrics(currentShopQueue || null);

      // 2. Fetch calendar
      const calendarRes = await fetch(`${API_URL}/api/calendar?shop_id=${shopId}&date=${date}`);
      if (!calendarRes.ok) throw new Error('API Calendar error');
      const calendarData = await calendarRes.json();
      
      setAppointments(calendarData.appointments || []);
      setIsFallbackMode(false);
    } catch (err) {
      console.warn("FastAPI backend is offline or unreachable. Loading fallback static mock data for demo...");
      setIsFallbackMode(true);
      
      // Fallback calculations
      const currentFallbackShop = FALLBACK_QUEUES.find((q) => q.shop_id === shopId);
      setQueueMetrics(currentFallbackShop || null);
      
      const shopAppointments = FALLBACK_CALENDAR[shopId] || [];
      setAppointments(shopAppointments);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [shopId, date]);

  // Trigger temporary notification toast
  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

  // Trigger action simulation
  const handleAction = (appId: number, clientHash: string, actionType: 'whatsapp' | 'confirm') => {
    if (actionType === 'whatsapp') {
      setTriggeredActions(prev => ({ ...prev, [appId]: 'whatsapp' }));
      triggerToast(`Recordatorio de WhatsApp enviado al cliente (Hash: ${clientHash})`);
    } else {
      setTriggeredActions(prev => ({ ...prev, [appId]: 'confirmed' }));
      triggerToast(`Turno #${appId} confirmado exitosamente y re-verificado.`);
    }
  };

  return (
    <div className="app-container">
      
      {/* Notification popup alert */}
      <ToastNotification message={toastMessage} />

      {/* Header controls & tabs section */}
      <Header 
        shopId={shopId}
        setShopId={setShopId}
        date={date}
        setDate={setDate}
        isFallbackMode={isFallbackMode}
        onRefresh={fetchData}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      {loading ? (
        <div className="loading-container">
          <div className="spinner"></div>
          <span style={{ marginLeft: '12px' }}>Cargando datos del panel...</span>
        </div>
      ) : (
        <main>
          {activeTab === 'agenda' ? (
            /* TAB 1: Agenda & Alerts (2-Column Grid) */
            <div className="view-grid-agenda fade-in">
              <AgendaTimeline 
                appointments={appointments} 
                triggeredActions={triggeredActions}
                selectedAppId={selectedAppId}
                onSelectApp={(id) => setSelectedAppId(prev => prev === id ? null : id)}
              />

              <AbsenteeismAlerts 
                appointments={appointments}
                triggeredActions={triggeredActions}
                handleAction={handleAction}
                selectedAppId={selectedAppId}
              />
            </div>
          ) : (
            /* TAB 2: Queuing Theory Detailed Analytics View */
            <QueueMetricsColumn 
              queueMetrics={queueMetrics}
              shopId={shopId}
            />
          )}
        </main>
      )}
    </div>
  );
}

export default App;
