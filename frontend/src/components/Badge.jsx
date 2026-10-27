import React from 'react';
import { CheckCircle2, AlertTriangle, Info, ShieldAlert } from 'lucide-react';

export default function Badge({ status, label, children }) {
  const normalized = (status || 'info').toLowerCase();

  let badgeClass = 'badge-info';
  let Icon = Info;

  if (normalized === 'verified' || normalized === 'safe' || normalized === 'success') {
    badgeClass = 'badge-verified';
    Icon = CheckCircle2;
  } else if (normalized === 'warning' || normalized === 'attention') {
    badgeClass = 'badge-warning';
    Icon = AlertTriangle;
  } else if (normalized === 'danger' || normalized === 'alert' || normalized === 'flagged') {
    badgeClass = 'badge-warning'; // Keep consistent styled warning/alert
    Icon = ShieldAlert;
  } else if (normalized === 'neutral') {
    badgeClass = 'badge-neutral';
    Icon = Info;
  }

  return (
    <span className={`badge ${badgeClass}`}>
      <Icon size={12} />
      <span>{label || children}</span>
    </span>
  );
}
