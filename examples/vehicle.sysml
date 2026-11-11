package VehicleModel {
  part def Vehicle {
    attribute mass : MassValue;
    attribute velocity : SpeedValue;
    part engine : Engine[1];
    part wheels : Wheel[4];
    port fuelIn : FuelPort;
    perform providePower;
  }
  part def Engine { attribute power : PowerValue; }
  part def Wheel { attribute diameter : LengthValue; }
  part vehicle_b : Vehicle {
    attribute :>> cargoMass;
  }
}
