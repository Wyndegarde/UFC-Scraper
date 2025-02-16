"use client";

import type { FightDetails } from "~/types/fights";

export function FightDetails({ fight }: { fight: FightDetails }) {
  return (
    <tr className="border-b">
      <td className="py-2">{fight.red_fighter}</td>
      <td className="py-2">{fight.blue_fighter}</td>
    </tr>
  );
}
