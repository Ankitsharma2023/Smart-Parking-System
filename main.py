import uuid
from enum import Enum, auto
from typing import Dict, List, Optional
import threading
import queue
import time
from dataclasses import dataclass, field

# Enum Definitions
class VehicleType(Enum):
    CAR = auto()
    MOTORCYCLE = auto()
    TRUCK = auto()

class SlotStatus(Enum):
    AVAILABLE = auto()
    OCCUPIED = auto()
    RESERVED = auto()

@dataclass
class Vehicle:
    """Represents a vehicle in the parking system"""
    vehicle_id: str
    license_plate: str
    vehicle_type: VehicleType
    owner_name: str
    entry_time: float = field(default_factory=time.time)
    parking_slot_id: Optional[str] = None

class ParkingSlot:
    """Represents an individual parking slot with linked list capabilities"""
    def __init__(self, slot_id: str, vehicle_type: VehicleType):
        self.slot_id = slot_id
        self.vehicle_type = vehicle_type
        self.status = SlotStatus.AVAILABLE
        self.vehicle = None
        self.next_slot = None  # For linked list implementation
        self.prev_slot = None  # For doubly linked list
        self.reservation_time = None

class User:
    """Represents a user in the parking system"""
    def __init__(self, name: str, contact: str):
        self.user_id = str(uuid.uuid4())
        self.name = name
        self.contact = contact
        self.vehicles: List[Vehicle] = []

    def add_vehicle(self, vehicle: Vehicle):
        """Add a vehicle to user's vehicle list"""
        self.vehicles.append(vehicle)

class ParkingLotManager:
    """Advanced Parking Lot Management System"""
    def __init__(self, slot_config: Dict[VehicleType, int]):
        # Concurrent access management
        self.lock = threading.Lock()
        
        # Users and vehicle management
        self.users: Dict[str, User] = {}
        
        # Slot management using linked list concept
        self.slots: Dict[VehicleType, List[ParkingSlot]] = {}
        self.total_slots: Dict[VehicleType, int] = {}
        
        # Initialize slots
        self._initialize_slots(slot_config)
    
    def _initialize_slots(self, slot_config: Dict[VehicleType, int]):
        """Initialize parking slots with linked list structure"""
        for vehicle_type, count in slot_config.items():
            self.total_slots[vehicle_type] = count
            self.slots[vehicle_type] = []
            
            for i in range(count):
                slot = ParkingSlot(
                    slot_id=f"{vehicle_type.name}_SLOT_{i+1}", 
                    vehicle_type=vehicle_type
                )
                
                # Create linked list structure
                if self.slots[vehicle_type]:
                    last_slot = self.slots[vehicle_type][-1]
                    last_slot.next_slot = slot
                    slot.prev_slot = last_slot
                
                self.slots[vehicle_type].append(slot)
    
    def register_user(self, name: str, contact: str) -> User:
        """Register a new user in the system"""
        user = User(name, contact)
        self.users[user.user_id] = user
        return user
    
    def find_available_slot(self, vehicle_type: VehicleType) -> Optional[ParkingSlot]:
        """Find first available slot for a specific vehicle type"""
        with self.lock:
            for slot in self.slots.get(vehicle_type, []):
                if slot.status == SlotStatus.AVAILABLE:
                    return slot
            return None
    
    def park_vehicle(self, vehicle: Vehicle) -> Optional[ParkingSlot]:
        """Park a vehicle in an available slot"""
        with self.lock:
            slot = self.find_available_slot(vehicle.vehicle_type)
            
            if slot:
                # Check if slots are full
                occupied_count = sum(1 for s in self.slots[vehicle.vehicle_type] 
                                     if s.status == SlotStatus.OCCUPIED)
                
                if occupied_count >= self.total_slots[vehicle.vehicle_type]:
                    print(f"No available slots for {vehicle.vehicle_type.name}")
                    return None
                
                # Park the vehicle
                slot.status = SlotStatus.OCCUPIED
                slot.vehicle = vehicle
                vehicle.parking_slot_id = slot.slot_id
                slot.reservation_time = time.time()
                
                return slot
            
            return None
    
    def remove_vehicle(self, slot_id: str) -> Optional[Vehicle]:
        """Remove a vehicle from a specific slot"""
        with self.lock:
            for vehicle_type_slots in self.slots.values():
                for slot in vehicle_type_slots:
                    if slot.slot_id == slot_id and slot.status == SlotStatus.OCCUPIED:
                        vehicle = slot.vehicle
                        slot.status = SlotStatus.AVAILABLE
                        slot.vehicle = None
                        slot.reservation_time = None
                        return vehicle
            return None
    
    def get_parking_fee(self, vehicle: Vehicle) -> float:
        """Calculate parking fee based on duration"""
        duration = time.time() - vehicle.entry_time
        hourly_rate = 5.0  # $5 per hour
        return max(hourly_rate * (duration / 3600), hourly_rate)

class SmartParkingSystem:
    """Interactive Parking System with Advanced Features"""
    def __init__(self, slot_config: Dict[VehicleType, int]):
        self.parking_lot = ParkingLotManager(slot_config)
        self.current_user = None
    
    def run_interactive_menu(self):
        """Main interactive menu for parking system"""
        while True:
            print("\n--- Smart Parking System ---")
            print("1. Register User")
            print("2. Add Vehicle")
            print("3. Park Vehicle")
            print("4. List Parked Vehicles")
            print("5. Exit Vehicle")
            print("6. Exit System")
            
            choice = input("Enter your choice (1-6): ")
            
            if choice == '1':
                self.register_user()
            elif choice == '2':
                self.add_vehicle()
            elif choice == '3':
                self.park_vehicle()
            elif choice == '4':
                self.list_parked_vehicles()
            elif choice == '5':
                self.exit_vehicle()
            elif choice == '6':
                break
            else:
                print("Invalid choice. Try again.")
    
    def register_user(self):
        """Register a new user"""
        name = input("Enter user name: ")
        contact = input("Enter contact number: ")
        user = self.parking_lot.register_user(name, contact)
        print(f"User {name} registered with ID: {user.user_id}")
        self.current_user = user
    
    def add_vehicle(self):
        """Add a vehicle to the current user"""
        if not self.current_user:
            print("Please register a user first.")
            return
        
        license_plate = input("Enter license plate: ")
        print("Select Vehicle Type:")
        for i, vtype in enumerate(VehicleType, 1):
            print(f"{i}. {vtype.name}")
        
        type_choice = int(input("Enter vehicle type number: "))
        vehicle_type = list(VehicleType)[type_choice - 1]
        
        vehicle = Vehicle(
            vehicle_id=str(uuid.uuid4()),
            license_plate=license_plate,
            vehicle_type=vehicle_type,
            owner_name=self.current_user.name
        )
        
        self.current_user.add_vehicle(vehicle)
        print(f"Vehicle {license_plate} added to user {self.current_user.name}")
    
    def park_vehicle(self):
        """Park a vehicle"""
        if not self.current_user or not self.current_user.vehicles:
            print("No vehicles to park. Add a vehicle first.")
            return
        
        print("Select a vehicle to park:")
        for i, vehicle in enumerate(self.current_user.vehicles, 1):
            print(f"{i}. {vehicle.license_plate} ({vehicle.vehicle_type.name})")
        
        choice = int(input("Enter vehicle number: ")) - 1
        vehicle = self.current_user.vehicles[choice]
        
        parked_slot = self.parking_lot.park_vehicle(vehicle)
        if parked_slot:
            print(f"Vehicle {vehicle.license_plate} parked in {parked_slot.slot_id}")
        else:
            print("Parking failed. No available slots.")
    
    def list_parked_vehicles(self):
        """List all currently parked vehicles"""
        print("\n--- Parked Vehicles ---")
        for vehicle_type, slots in self.parking_lot.slots.items():
            print(f"\n{vehicle_type.name} Slots:")
            for slot in slots:
                if slot.status == SlotStatus.OCCUPIED:
                    vehicle = slot.vehicle
                    print(f"Slot: {slot.slot_id}, Vehicle: {vehicle.license_plate}, Owner: {vehicle.owner_name}")
    
    def exit_vehicle(self):
        """Remove a parked vehicle"""
        self.list_parked_vehicles()
        slot_id = input("Enter slot ID to remove vehicle: ")
        
        vehicle = self.parking_lot.remove_vehicle(slot_id)
        if vehicle:
            fee = self.parking_lot.get_parking_fee(vehicle)
            print(f"Vehicle {vehicle.license_plate} exited. Parking fee: ${fee:.2f}")
        else:
            print("No vehicle found in the specified slot.")

def main():
    # Configure initial parking lot slots
    slot_config = {
        VehicleType.CAR: 5,
        VehicleType.MOTORCYCLE: 3,
        VehicleType.TRUCK: 2
    }
    
    parking_system = SmartParkingSystem(slot_config)
    parking_system.run_interactive_menu()

if __name__ == "__main__":
    main()