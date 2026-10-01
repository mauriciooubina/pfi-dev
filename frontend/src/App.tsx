import { useState, useEffect } from 'react';
import { Header } from '@/components/Header';
import { QueueMetricsColumn } from '@/components/QueueMetricsColumn';
import { AgendaTimeline } from '@/components/AgendaTimeline';
import { AbsenteeismAlerts } from '@/components/AbsenteeismAlerts';
import { ToastNotification } from '@/components/ToastNotification';
import { FALLBACK_QUEUES, FALLBACK_CALENDAR } from '@/data/fallbackData';
import type { ShopQueueData, Appointment } from '@/types';
import '@/styles/App.css';

const DEFAULT_DATES: Record<'hellfish' | 'hooligans', string> = {
  hooligans: '2026-01-21',
  hellfish: '2026-06-04'
};

function App() {
  const [shopId, setShopId] = useState<'hellfish' | 'hooligans'>('hooligans');
  const [date, setDate] = useState<string>(DEFAULT_DATES['hooligans']);
  const [activeTab, setActiveTab] = useState<'agenda' | 'queues'>('agenda');
  
  const [loading, setLoading] = useState<boolean>(true);
  const [isFallbackMode, setIsFallbackMode] = useState<boolean>(false);
  
  const [queueMetrics, setQueueMetrics] = useState<ShopQueueData | null>(null);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [selectedAppId, setSelectedAppId] = useState<number | null>(null);
  
  const [triggeredActions, setTriggeredActions] = useState<Record<number, string>>({});
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleShopChange = (newShop: 'hellfish' | 'hooligans') => {
    setShopId(newShop);
    setDate(DEFAULT_DATES[newShop]);
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const queuesRes = await fetch(`${API_URL}/api/queues`);
      if (!queuesRes.ok) throw new Error('API Queues error');
      const queuesData: ShopQueueData[] = await queuesRes.json();
      
      const currentShopQueue = queuesData.find((q) => q.shop_id === shopId);
      setQueueMetrics(currentShopQueue || null);

      const calendarRes = await fetch(`${API_URL}/api/calendar?shop_id=${shopId}&date=${date}`);
      if (!calendarRes.ok) throw new Error('API Calendar error');
      const calendarData = await calendarRes.json();
      
      setAppointments(calendarData.appointments || []);
      setIsFallbackMode(false);
    } catch (err) {
      console.warn("FastAPI backend is offline or unreachable. Loading fallback static mock data for demo...");
      setIsFallbackMode(true);
      
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

  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 4000);
  };

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
        setShopId={handleShopChange}
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
