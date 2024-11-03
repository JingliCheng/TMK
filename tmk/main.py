import argparse
from tmk.set_config import Config
from tmk.utils import setup_directories, scrape_subreddits, rank_and_report
from tmk.processor import process_raw_data

def main():
    parser = argparse.ArgumentParser(description='TMK: Clinical Trial Recruitment System')
    parser.add_argument('--config', default='config/default_config.yaml', 
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = Config(args.config)
        
        # Setup directories
        setup_directories(config)
        
        # Step 1: Scrape data
        scrape_subreddits(config)
        
        # Step 2: Process data and update database
        process_raw_data(
            raw_data_dir=config.directories['raw_data'],
            processed_dir=config.directories['processed_data'],
            db_path=f"{config.directories['data']}/users.pkl",
            config=config
        )
        
        # Step 3: Generate ranking reports
        rank_and_report(config)
        
        print("\nProcessing completed successfully!")
        
    except Exception as e:
        print(f"\nError during processing: {e}")
        raise

if __name__ == "__main__":
    main() 