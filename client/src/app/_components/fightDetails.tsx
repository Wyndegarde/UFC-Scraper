"use client";

import type { FightDetails } from "~/types/fights";

export function FightDetails({ fight }: { fight: FightDetails }) {
  return (
    <>
      <h2>{fight.red_fighter}</h2>
      <h2>{fight.blue_fighter}</h2>
    </>
  );
}
