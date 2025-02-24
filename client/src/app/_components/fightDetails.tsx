"use client";

import type { FightDetails } from "~/types/fights";

export function FightDetails({ fight }: { fight: FightDetails }) {
  return (
    <tr className="hover:bg-gray-50/50 transition-colors">
      <td className={`px-6 py-4 text-sm ${fight.predicted_winner === fight.red_fighter ? "text-green-600 font-medium" : ""}`}>
        {fight.red_fighter}
      </td>
      <td className={`px-6 py-4 text-sm ${fight.predicted_winner === fight.blue_fighter ? "text-green-600 font-medium" : ""}`}>
        {fight.blue_fighter}
      </td>
    </tr>
  );
}
