import { ReactNode, useMemo, useState } from 'react';

import { useAuth } from '../auth/AuthContext';
import { AcademicPage } from '../features/academic/AcademicPage';
import { AdmissionsPage } from '../features/admissions/AdmissionsPage';
import { AttendancePage } from '../features/attendance/AttendancePage';
import { CertificatesPage } from '../features/certificates/CertificatesPage';
import { ExaminationPage } from '../features/examinations/ExaminationPage';
import { FinancePage } from '../features/fees/FinancePage';
import { GradeCalculationPage } from '../features/grade-calculations/GradeCalculationPage';
import { LoginPage } from '../features/authentication/LoginPage';
import { MarksEntryPage } from '../features/marks-entry/MarksEntryPage';
import { MeritListsPage } from '../features/merit-lists/MeritListsPage';
import { NotificationsPage } from '../features/notifications/NotificationsPage';
import { PortalsPage } from '../features/portals/PortalsPage';
import { ReportCardsPage } from '../features/report-cards/ReportCardsPage';
import { ReportingPage } from '../features/reporting/ReportingPage';
import { ResultProcessingPage } from '../features/results/ResultProcessingPage';
import { SetupPage } from '../features/settings/SetupPage';
import { StudentPage } from '../features/students/StudentPage';
import { TimetablePage } from '../features/timetable/TimetablePage';
import { TranscriptsPage } from '../features/transcripts/TranscriptsPage';

type ModuleKey =
  | 'setup' | 'academic' | 'admissions' | 'students' | 'timetable' | 'attendance'
  | 'examinations' | 'marks' | 'results' | 'grades' | 'report-cards' | 'merit'
  | 'transcripts' | 'finance' | 'portals' | 'notifications' | 'certificates' | 'reports';

const navigation: Array<{ group: string; items: Array<{ key: ModuleKey; label: string }> }> = [
  { group: 'Institution', items: [
    { key: 'setup', label: 'Institution setup' },
    { key: 'academic', label: 'Academic structure' },
    { key: 'admissions', label: 'Admissions' },
    { key: 'students', label: 'Students' },
  ] },
  { group: 'Teaching', items: [
    { key: 'timetable', label: 'Timetable' },
    { key: 'attendance', label: 'Attendance' },
    { key: 'examinations', label: 'Examinations' },
    { key: 'marks', label: 'Marks entry' },
  ] },
  { group: 'Results', items: [
    { key: 'results', label: 'Result processing' },
    { key: 'grades', label: 'GPA & percentage' },
    { key: 'report-cards', label: 'Report cards' },
    { key: 'merit', label: 'Merit lists' },
    { key: 'transcripts', label: 'Transcripts' },
  ] },
  { group: 'Operations', items: [
    { key: 'finance', label: 'Finance' },
    { key: 'portals', label: 'User portals' },
    { key: 'notifications', label: 'Notifications' },
    { key: 'certificates', label: 'Certificates' },
    { key: 'reports', label: 'Reports & analytics' },
  ] },
];

const moduleTitles: Record<ModuleKey, string> = Object.fromEntries(
  navigation.flatMap((section) => section.items.map((item) => [item.key, item.label])),
) as Record<ModuleKey, string>;

export function App() {
  const { authenticated, profile, logout } = useAuth();
  const [selected, setSelected] = useState<ModuleKey>('setup');
  const [menuOpen, setMenuOpen] = useState(false);

  const content = useMemo<Record<ModuleKey, ReactNode>>(() => ({
    setup: <SetupPage />,
    academic: <AcademicPage />,
    admissions: <AdmissionsPage />,
    students: <StudentPage />,
    timetable: <TimetablePage />,
    attendance: <AttendancePage />,
    examinations: <ExaminationPage />,
    marks: <MarksEntryPage />,
    results: <ResultProcessingPage />,
    grades: <GradeCalculationPage />,
    'report-cards': <ReportCardsPage />,
    merit: <MeritListsPage />,
    transcripts: <TranscriptsPage />,
    finance: <FinancePage />,
    portals: <PortalsPage />,
    notifications: <NotificationsPage />,
    certificates: <CertificatesPage />,
    reports: <ReportingPage />,
  }), []);

  if (!authenticated) return <LoginPage />;

  function selectModule(key: ModuleKey) {
    setSelected(key);
    setMenuOpen(false);
  }

  return (
    <div className="erp-shell">
      <aside className={`sidebar ${menuOpen ? 'sidebar-open' : ''}`}>
        <div className="sidebar-brand">
          <div className="brand-mark small">BSC</div>
          <div><strong>College ERP</strong><span>Administration</span></div>
        </div>
        <nav aria-label="ERP modules">
          {navigation.map((section) => (
            <div className="nav-group" key={section.group}>
              <p>{section.group}</p>
              {section.items.map((item) => (
                <button
                  className={selected === item.key ? 'active' : ''}
                  key={item.key}
                  onClick={() => selectModule(item.key)}
                >
                  {item.label}
                </button>
              ))}
            </div>
          ))}
        </nav>
      </aside>
      {menuOpen && <button className="sidebar-scrim" aria-label="Close menu" onClick={() => setMenuOpen(false)} />}
      <section className="workspace">
        <header className="topbar">
          <button className="menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label="Open menu">☰</button>
          <div><p className="eyebrow">Brilliant Science College</p><h1>{moduleTitles[selected]}</h1></div>
          <div className="account">
            <div><strong>{profile?.username}</strong><span>{profile?.college_id}</span></div>
            <button className="secondary-button" onClick={() => void logout()}>Sign out</button>
          </div>
        </header>
        <main className="page-content">{content[selected]}</main>
      </section>
    </div>
  );
}
