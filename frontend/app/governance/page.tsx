/**
 * DIOTEC 360 IA - Governance Page v10.3.1
 * 
 * Desktop governance interface for Genesis Authority
 * Access at: diotec360.com/governance
 */

import DesktopGovernancePanel from '@/components/DesktopGovernancePanel';
import LatticeWallet from '@/components/LatticeWallet';

export default function GovernancePage() {
  return (
    <div className="min-h-screen bg-gray-950">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 p-6">
        {/* Main Governance Panel */}
        <div className="lg:col-span-2">
          <DesktopGovernancePanel />
        </div>
        
        {/* Sidebar with Wallet */}
        <div className="lg:col-span-1">
          <div className="sticky top-6">
            <LatticeWallet />
          </div>
        </div>
      </div>
    </div>
  );
}
