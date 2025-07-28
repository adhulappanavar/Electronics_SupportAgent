import os
from pathlib import Path

def create_sample_data():
    """Create sample SOPs and FAQs for testing the knowledge base"""
    
    # Create directories
    base_dir = Path("sample_data")
    brands = ["Samsung", "LG"]
    products = ["TV", "Refrigerator", "Washing_Machine", "Speaker"]
    doc_types = ["SOP", "FAQ", "Manual"]
    
    for brand in brands:
        for product in products:
            for doc_type in doc_types:
                dir_path = base_dir / brand / product / doc_type
                dir_path.mkdir(parents=True, exist_ok=True)
    
    # Samsung TV Documents
    samsung_tv_sop = """
# Samsung TV Standard Operating Procedure

## Initial Setup Procedure
1. Unpack the TV from the box carefully
2. Attach the stand or mount to wall bracket
3. Connect power cable to outlet
4. Press power button on remote or TV
5. Follow on-screen setup wizard
6. Connect to WiFi network
7. Update firmware if prompted
8. Complete channel scan for cable/antenna

## Daily Operation
- Use Samsung Smart Remote for navigation
- Voice control available with Bixby
- SmartThings app integration for mobile control
- Gaming mode available for reduced input lag

## Maintenance Schedule
- Clean screen weekly with microfiber cloth
- Check for software updates monthly
- Inspect cables quarterly
- Professional service annually

## Error Code Reference
- Error 001: Network connection issue
- Error 012: Software update failure
- Error 105: HDMI connection problem
"""

    samsung_tv_faq = """
# Samsung TV Frequently Asked Questions

## Q: How do I connect my Samsung TV to WiFi?
A: Go to Settings > Network > Open Network Settings. Select your WiFi network and enter password. The TV will automatically connect.

## Q: Why is my Samsung TV not turning on?
A: Check these steps:
1. Ensure power cable is properly connected
2. Try different power outlet
3. Check if power LED is lit
4. Replace remote batteries
5. Contact support if issue persists

## Q: How do I update my Samsung TV software?
A: Go to Settings > Support > Software Update > Update Now. Ensure stable internet connection during update.

## Q: My Samsung TV picture is blurry, what should I do?
A: 
1. Check input source quality
2. Adjust picture settings in Settings > Picture
3. Ensure proper viewing distance
4. Check cable connections
5. Reset picture settings to default

## Q: How do I use Samsung SmartThings with my TV?
A: Download SmartThings app, ensure TV and phone are on same network, tap "Add Device" and follow instructions.

## Q: What gaming features are available?
A: Samsung TVs support:
- Game Mode for reduced input lag
- Variable Refresh Rate (VRR)
- Auto Low Latency Mode (ALLM)
- FreeSync Premium for smooth gaming
"""

    lg_fridge_sop = """
# LG Refrigerator Standard Operating Procedure

## Installation Procedure
1. Position refrigerator away from heat sources
2. Leave 2 inches clearance on sides, 4 inches on top
3. Level the refrigerator using adjustable feet
4. Wait 4 hours before plugging in (if transported horizontally)
5. Set initial temperature: Refrigerator 37°F, Freezer 0°F
6. Allow 24 hours to reach optimal temperature

## Daily Operation
- Fresh food compartment: 32-40°F
- Freezer compartment: -5 to 5°F
- Check door seals regularly
- Clean spills immediately
- Rotate food items (first in, first out)

## Maintenance Schedule
- Clean interior monthly
- Replace water filter every 6 months
- Clean condenser coils every 6 months
- Check and clean door gaskets quarterly
- Professional inspection annually

## Energy Saving Tips
- Keep doors closed as much as possible
- Don't overfill compartments
- Set appropriate temperatures
- Clean condenser coils regularly
- Check door seals for air leaks
"""

    lg_washer_faq = """
# LG Washing Machine Frequently Asked Questions

## Q: Why is my LG washer not spinning?
A: Common causes:
1. Unbalanced load - redistribute clothes evenly
2. Overloaded machine - remove some items
3. Door not properly closed - ensure secure closure
4. Clogged drain filter - clean filter
5. Contact service if problem persists

## Q: How much detergent should I use?
A: Use HE (High Efficiency) detergent only. Amount depends on load size:
- Small load: 1 tablespoon
- Medium load: 2 tablespoons  
- Large load: 3 tablespoons
- Heavily soiled: Add extra tablespoon

## Q: What do the error codes mean?
A: Common LG washer error codes:
- IE: Water inlet error - check water supply
- OE: Drain error - check drain hose/filter
- UE: Unbalanced load - redistribute clothes
- LE: Motor error - contact service
- PE: Water level sensor error - contact service

## Q: How do I clean my LG washer?
A: Run monthly cleaning cycle:
1. Remove all clothes
2. Add washing machine cleaner or 2 cups white vinegar
3. Run "Tub Clean" cycle
4. Wipe drum and door seal
5. Leave door open to air dry

## Q: Why are my clothes still wet after wash cycle?
A: Check:
1. Proper spin cycle selected
2. Balanced load distribution
3. Drain hose not kinked
4. Clean drain filter
5. Washer level and stable
"""

    samsung_speaker_manual = """
# Samsung Speaker User Manual

## Package Contents
- Samsung Speaker
- Power adapter
- Audio cable (3.5mm)
- Quick setup guide
- Warranty information

## Setup Instructions
1. Connect power adapter to speaker
2. Press and hold power button for 3 seconds
3. Speaker will enter pairing mode (blue LED flashing)
4. On your device, enable Bluetooth
5. Select "Samsung Speaker" from available devices
6. LED will turn solid blue when connected

## Controls
- Power: Long press power button
- Play/Pause: Single press power button
- Volume: Use + and - buttons
- Skip tracks: Double/triple press power button
- Bluetooth pairing: Hold power + volume up

## Connectivity Options
- Bluetooth 5.0 (primary)
- 3.5mm auxiliary input
- USB-C for charging/audio
- Wi-Fi for Samsung SmartThings integration

## Specifications
- Frequency response: 20Hz - 20kHz
- Battery life: Up to 12 hours
- Charging time: 3 hours
- Bluetooth range: 30 feet
- Water resistance: IPX5 rated

## Troubleshooting
- No sound: Check volume levels and connections
- Won't pair: Clear Bluetooth cache, restart devices
- Poor audio quality: Move closer to source device
- Won't charge: Check charging cable and port
"""

    # Write files
    file_data = [
        ("Samsung/TV/SOP/tv_setup_procedure.txt", samsung_tv_sop),
        ("Samsung/TV/FAQ/tv_common_questions.txt", samsung_tv_faq),
        ("LG/Refrigerator/SOP/fridge_installation.txt", lg_fridge_sop),
        ("LG/Washing_Machine/FAQ/washer_troubleshooting.txt", lg_washer_faq),
        ("Samsung/Speaker/Manual/speaker_user_guide.txt", samsung_speaker_manual),
    ]
    
    for file_path, content in file_data:
        full_path = base_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("Sample data created successfully!")
    print(f"Created {len(file_data)} sample documents in {base_dir}")
    
    return base_dir

if __name__ == "__main__":
    create_sample_data() 