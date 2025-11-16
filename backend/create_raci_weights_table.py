"""
Script to create RACI Weights Configuration table and initialize with default values
"""
from app import create_app, db
from app.models.raci_weights_config import RaciWeightsConfig

def create_raci_weights_table():
    """Create RACI Weights Configuration table"""
    app = create_app()
    
    with app.app_context():
        # Create the table
        db.create_all()
        print("✓ RACI Weights Configuration table created")
        
        # Check if configuration already exists
        config = RaciWeightsConfig.query.first()
        
        if config:
            print("✓ RACI Weights Configuration already exists:")
            print(f"  Workload weights: R={config.responsible_workload}, A={config.accountable_workload}, C={config.consulted_workload}, I={config.informed_workload}")
            print(f"  Duration weights: R={config.responsible_duration}, A={config.accountable_duration}, C={config.consulted_duration}, I={config.informed_duration}")
        else:
            # Create default configuration
            config = RaciWeightsConfig(
                responsible_workload=1.0,
                accountable_workload=0.1,
                consulted_workload=0.05,
                informed_workload=0.01,
                responsible_duration=1.0,
                accountable_duration=0.1,
                consulted_duration=0.05,
                informed_duration=0.01
            )
            db.session.add(config)
            db.session.commit()
            print("✓ Default RACI Weights Configuration created:")
            print(f"  Workload weights: R=1.0, A=0.1, C=0.05, I=0.01")
            print(f"  Duration weights: R=1.0, A=0.1, C=0.05, I=0.01")

if __name__ == '__main__':
    create_raci_weights_table()

