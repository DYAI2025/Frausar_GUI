"""
Manages the loading and selection of analysis profiles from a central registry.
"""
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

class ProfileManager:
    """
    Handles the analysis profile registry, allowing for selection based on
    tags or a specific profile ID.
    """
    def __init__(self, registry_path: Path):
        """
        Initializes the ProfileManager with the path to the registry file.

        :param registry_path: Path to the 'registry.yaml' file.
        """
        if not registry_path.exists():
            raise FileNotFoundError(f"Registry file not found at: {registry_path}")
        self.registry_path = registry_path
        self.base_dir = registry_path.parent
        self._registry: Dict[str, Any] = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """Loads the YAML registry file."""
        with open(self.registry_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def find_profiles_by_tags(self, *tags: str) -> List[Dict[str, Any]]:
        """
        Finds all profiles that match a given set of tags.

        :param tags: A variable number of tag strings to search for.
        :return: A list of profile dictionaries that contain all specified tags.
        """
        if not tags:
            return self._registry.get('schemas', [])
        
        required_tags = set(tag.lower() for tag in tags)
        
        matching_profiles = [
            profile for profile in self._registry.get('schemas', [])
            if required_tags.issubset(set(t.lower() for t in profile.get('focus_tags', [])))
        ]
        return matching_profiles

    def load_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        """
        Loads a specific profile by its ID and merges it with its template content.

        :param profile_id: The unique ID of the profile (e.g., 'REL_CRISIS').
        :return: A dictionary containing the merged profile and template data, or None if not found.
        """
        profile_info = next((p for p in self._registry.get('schemas', []) if p.get('id') == profile_id), None)

        if not profile_info:
            return None

        template_path = self.base_dir / profile_info.get('template_file')
        if not template_path.exists():
            print(f"Warning: Template file '{template_path}' for profile '{profile_id}' not found.")
            return profile_info # Return profile info without template

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = yaml.safe_load(f)
        
        # Merge template content into the profile information
        # The template is the base, and the profile info can override/add to it.
        merged_profile = {**template_content, **profile_info}
        
        return merged_profile

# Example Usage
if __name__ == '__main__':
    try:
        # Assuming the script is run from the project root or a context where the path is correct
        registry_file = Path('Marker_assist_bot/Schema_LOADER/registry.yaml')
        manager = ProfileManager(registry_file)

        print("--- Finding profiles by tags 'crisis' and 'relationship' ---")
        profiles = manager.find_profiles_by_tags("crisis", "relationship")
        if profiles:
            for p in profiles:
                print(f"  - Found profile: {p['name']} (ID: {p['id']})")
            
            # Load the first found profile
            profile_id_to_load = profiles[0]['id']
            print(f"\n--- Loading profile '{profile_id_to_load}' ---")
            loaded_profile = manager.load_profile(profile_id_to_load)

            if loaded_profile:
                print("\n--- Loaded Profile Content (merged with template) ---")
                # Using yaml.dump to pretty-print the dictionary
                print(yaml.dump(loaded_profile, sort_keys=False, allow_unicode=True))
            else:
                print(f"Could not load profile with ID: {profile_id_to_load}")

        else:
            print("No profiles found matching the tags.")

        print("\n--- Listing all available profiles ---")
        all_profiles = manager.find_profiles_by_tags()
        for p in all_profiles:
            print(f"  - {p['id']}: {p['name']}")

    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure the registry.yaml exists at the specified path.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}") 