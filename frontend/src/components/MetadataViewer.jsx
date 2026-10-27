import React, { useState } from 'react';
import { FileText, Camera, Clock, MapPin, Database, ExternalLink, Info } from 'lucide-react';

export default function MetadataViewer({ metadata }) {
  const [activeTab, setActiveTab] = useState('file');

  if (!metadata) {
    return <div style={{ color: 'var(--text-muted)' }}>No metadata available for this record.</div>;
  }

  const { file_info = {}, camera_info = {}, timestamp_info = {}, gps_info = {}, raw_exif = {} } = metadata;

  const rawTagsCount = Object.keys(raw_exif).length;

  return (
    <div className="card" style={{ marginTop: '1.5rem' }}>
      <div className="card-header">
        <h3 className="card-title">
          <Database size={18} color="var(--accent-blue)" />
          Extracted Forensic Metadata
        </h3>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          {metadata.has_exif ? `${rawTagsCount} EXIF tags decoded` : 'No EXIF header'}
        </span>
      </div>

      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'file' ? 'active' : ''}`}
          onClick={() => setActiveTab('file')}
        >
          <FileText size={14} style={{ display: 'inline', marginRight: 6 }} />
          File Properties
        </button>
        <button 
          className={`tab-btn ${activeTab === 'camera' ? 'active' : ''}`}
          onClick={() => setActiveTab('camera')}
        >
          <Camera size={14} style={{ display: 'inline', marginRight: 6 }} />
          Camera & Optics
        </button>
        <button 
          className={`tab-btn ${activeTab === 'timestamps' ? 'active' : ''}`}
          onClick={() => setActiveTab('timestamps')}
        >
          <Clock size={14} style={{ display: 'inline', marginRight: 6 }} />
          Timestamps
        </button>
        <button 
          className={`tab-btn ${activeTab === 'gps' ? 'active' : ''}`}
          onClick={() => setActiveTab('gps')}
        >
          <MapPin size={14} style={{ display: 'inline', marginRight: 6 }} />
          GPS Location {gps_info.has_gps && <span style={{ color: 'var(--color-success)', marginLeft: 4 }}>●</span>}
        </button>
        <button 
          className={`tab-btn ${activeTab === 'raw' ? 'active' : ''}`}
          onClick={() => setActiveTab('raw')}
        >
          <Database size={14} style={{ display: 'inline', marginRight: 6 }} />
          All Raw EXIF ({rawTagsCount})
        </button>
      </div>

      {/* Tab 1: File Properties */}
      {activeTab === 'file' && (
        <div className="kv-grid">
          <div className="kv-item">
            <div className="kv-label">Filename</div>
            <div className="kv-value">{file_info.filename || 'N/A'}</div>
          </div>
          <div className="kv-item">
            <div className="kv-label">Format / Extension</div>
            <div className="kv-value">{file_info.format || 'N/A'} ({file_info.extension || 'N/A'})</div>
          </div>
          <div className="kv-item">
            <div className="kv-label">File Size</div>
            <div className="kv-value">{file_info.size_formatted} ({file_info.size_bytes?.toLocaleString()} bytes)</div>
          </div>
          <div className="kv-item">
            <div className="kv-label">Dimensions</div>
            <div className="kv-value">{file_info.width} x {file_info.height} px</div>
          </div>
          <div className="kv-item">
            <div className="kv-label">Resolution / Megapixels</div>
            <div className="kv-value">{file_info.megapixels || 'N/A'}</div>
          </div>
          <div className="kv-item">
            <div className="kv-label">Aspect Ratio</div>
            <div className="kv-value">{file_info.aspect_ratio || 'N/A'}</div>
          </div>
          <div className="kv-item">
            <div className="kv-label">Color Mode</div>
            <div className="kv-value">{file_info.mode || 'N/A'}</div>
          </div>
          <div className="kv-item">
            <div className="kv-label">Filesystem Ingestion Date</div>
            <div className="kv-value">{file_info.fs_modified || 'N/A'}</div>
          </div>
        </div>
      )}

      {/* Tab 2: Camera & Optics */}
      {activeTab === 'camera' && (
        <div>
          {!metadata.has_exif && (
            <div className="alert" style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-light)', marginBottom: '1rem' }}>
              <Info size={16} color="var(--accent-blue)" />
              <span>No hardware metadata found. This image was either created by software or compressed through a messaging platform.</span>
            </div>
          )}
          <div className="kv-grid">
            <div className="kv-item">
              <div className="kv-label">Camera Make</div>
              <div className="kv-value" style={{ color: camera_info.make ? 'var(--text-main)' : 'var(--text-subtle)' }}>
                {camera_info.make || 'Not Recorded'}
              </div>
            </div>
            <div className="kv-item">
              <div className="kv-label">Camera Model</div>
              <div className="kv-value" style={{ color: camera_info.model ? 'var(--text-main)' : 'var(--text-subtle)' }}>
                {camera_info.model || 'Not Recorded'}
              </div>
            </div>
            <div className="kv-item">
              <div className="kv-label">Software Signature</div>
              <div className="kv-value" style={{ color: camera_info.software ? 'var(--accent-blue)' : 'var(--text-subtle)' }}>
                {camera_info.software || 'None Recorded'}
              </div>
            </div>
            <div className="kv-item">
              <div className="kv-label">Lens Model</div>
              <div className="kv-value">{camera_info.lens_model || 'N/A'}</div>
            </div>
            <div className="kv-item">
              <div className="kv-label">Focal Length</div>
              <div className="kv-value">{camera_info.focal_length || 'N/A'}</div>
            </div>
            <div className="kv-item">
              <div className="kv-label">F-Number (Aperture)</div>
              <div className="kv-value">{camera_info.f_number || 'N/A'}</div>
            </div>
            <div className="kv-item">
              <div className="kv-label">Exposure Time (Shutter)</div>
              <div className="kv-value">{camera_info.exposure_time || 'N/A'}</div>
            </div>
            <div className="kv-item">
              <div className="kv-label">ISO Sensitivity</div>
              <div className="kv-value">{camera_info.iso || 'N/A'}</div>
            </div>
            <div className="kv-item">
              <div className="kv-label">Flash State</div>
              <div className="kv-value">{camera_info.flash !== null ? String(camera_info.flash) : 'N/A'}</div>
            </div>
            <div className="kv-item">
              <div className="kv-label">Orientation</div>
              <div className="kv-value">{camera_info.orientation || 'Standard (1)'}</div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Timestamps */}
      {activeTab === 'timestamps' && (
        <div>
          <div className="kv-grid">
            <div className="kv-item">
              <div className="kv-label">DateTimeOriginal (Capture Time)</div>
              <div className="kv-value" style={{ color: timestamp_info.datetime_original ? 'var(--color-success)' : 'var(--text-subtle)' }}>
                {timestamp_info.datetime_original || 'Not Found'}
              </div>
            </div>
            <div className="kv-item">
              <div className="kv-label">DateTimeDigitized</div>
              <div className="kv-value">{timestamp_info.datetime_digitized || 'Not Found'}</div>
            </div>
            <div className="kv-item">
              <div className="kv-label">DateTime (EXIF Modification)</div>
              <div className="kv-value">{timestamp_info.datetime_modified || 'Not Found'}</div>
            </div>
            <div className="kv-item">
              <div className="kv-label">File System Timestamp</div>
              <div className="kv-value">{file_info.fs_modified || 'N/A'}</div>
            </div>
          </div>
          <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <strong>Forensics Note:</strong> In authentic camera captures, DateTimeOriginal and DateTimeDigitized typically match. If DateTime differs, the file was modified or re-saved after shutter capture.
          </div>
        </div>
      )}

      {/* Tab 4: GPS Geolocation */}
      {activeTab === 'gps' && (
        <div>
          {gps_info.has_gps ? (
            <div>
              <div className="kv-grid" style={{ marginBottom: '1.25rem' }}>
                <div className="kv-item">
                  <div className="kv-label">Decimal Latitude</div>
                  <div className="kv-value" style={{ color: 'var(--accent-blue)', fontFamily: 'var(--font-mono)' }}>
                    {gps_info.latitude}°
                  </div>
                </div>
                <div className="kv-item">
                  <div className="kv-label">Decimal Longitude</div>
                  <div className="kv-value" style={{ color: 'var(--accent-blue)', fontFamily: 'var(--font-mono)' }}>
                    {gps_info.longitude}°
                  </div>
                </div>
                <div className="kv-item">
                  <div className="kv-label">DMS Coordinates</div>
                  <div className="kv-value">{gps_info.dms_latitude}, {gps_info.dms_longitude}</div>
                </div>
                <div className="kv-item">
                  <div className="kv-label">Altitude</div>
                  <div className="kv-value">{gps_info.altitude || 'N/A'}</div>
                </div>
                <div className="kv-item">
                  <div className="kv-label">GPS Satellite Timestamp</div>
                  <div className="kv-value">{gps_info.gps_timestamp || 'N/A'}</div>
                </div>
              </div>

              {gps_info.maps_url && (
                <a 
                  href={gps_info.maps_url} 
                  target="_blank" 
                  rel="noreferrer" 
                  className="btn btn-primary"
                  style={{ fontSize: '0.85rem' }}
                >
                  <MapPin size={14} />
                  <span>View Location on Google Maps</span>
                  <ExternalLink size={12} style={{ marginLeft: 4 }} />
                </a>
              )}
            </div>
          ) : (
            <div style={{ padding: '1.5rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
              <MapPin size={32} color="var(--text-subtle)" style={{ marginBottom: '0.5rem' }} />
              <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '0.25rem' }}>No GPS Geolocation Recorded</div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '500px', margin: '0 auto' }}>
                GPS coordinates are optional in digital imagery. Many cameras lack hardware GPS chips, and smartphones frequently suppress GPS coordinates for user privacy. Absence of GPS does not indicate file tampering.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Tab 5: All Raw EXIF */}
      {activeTab === 'raw' && (
        <div>
          {rawTagsCount > 0 ? (
            <div className="data-table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th style={{ width: '35%' }}>EXIF Tag Identifier</th>
                    <th>Extracted Raw Value</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(raw_exif).map(([tagKey, tagVal]) => (
                    <tr key={tagKey}>
                      <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-blue)', fontWeight: 500 }}>
                        {tagKey}
                      </td>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--text-main)' }}>
                        {typeof tagVal === 'object' ? JSON.stringify(tagVal) : String(tagVal)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div style={{ padding: '1.5rem', background: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', textAlign: 'center', color: 'var(--text-muted)' }}>
              No raw EXIF tags were present in this image file.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
