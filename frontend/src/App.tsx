import Header from './components/Header';
import ComplaintForm from './components/ComplaintForm';
import AIAssistantPanel from './components/AIAssistantPanel';

function App() {
  return (
    <div className="h-screen bg-slate-50 text-slate-800 flex flex-col font-sans overflow-hidden">
      <Header />
      <main className="flex-1 max-w-[1600px] w-full mx-auto p-4 lg:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 min-h-0">
        {/* Left Panel — Complaint Form */}
        <div className="lg:col-span-7 xl:col-span-7 flex flex-col min-h-0 bg-white rounded-xl shadow-sm border border-slate-200 overflow-y-auto">
          <ComplaintForm />
        </div>
        {/* Right Panel — AI Copilot */}
        <div className="lg:col-span-5 xl:col-span-5 flex flex-col min-h-0">
          <AIAssistantPanel />
        </div>
      </main>
    </div>
  );
}

export default App;
