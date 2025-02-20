export type FightDetails = {
    red_fighter: string;
    blue_fighter: string;
    predicted_winner: string;
}

export type FightsProps = {
  fights: FightDetails[];
}