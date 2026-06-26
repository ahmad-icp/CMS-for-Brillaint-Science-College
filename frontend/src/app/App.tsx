const modules = [
  'Authentication',
  'Admissions',
  'Student Information System',
  'Attendance',
  'Examination',
  'Fee Management',
  'Reports',
  'Notifications',
  'Backup Manager',
  'AI Analytics',
];

export function App() {
  return (
    <main style={{ fontFamily: 'Inter, system-ui, sans-serif', padding: '2rem' }}>
      <h1>College ERP Platform</h1>
      <p>Multi-tenant ERP foundation for configurable colleges and schools.</p>
      <h2>Module Roadmap</h2>
      <ul>
        {modules.map((module) => (
          <li key={module}>{module}</li>
        ))}
      </ul>
    </main>
  );
}
