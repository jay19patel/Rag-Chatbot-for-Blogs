import json
from typing import Dict, Any, List, Optional
import os

class PersonalContextManager:
    def __init__(self, personal_info_path: str = "personal_info.json"):
        self.personal_info_path = personal_info_path
        self.personal_data = {}
        self.load_personal_info()
    
    def load_personal_info(self):
        """Load personal information from JSON file"""
        try:
            with open(self.personal_info_path, 'r', encoding='utf-8') as f:
                self.personal_data = json.load(f)
            print("👤 Personal context loaded successfully")
        except FileNotFoundError:
            print("⚠️ Personal info file not found, using default data")
            self.personal_data = self._default_personal_info()
        except json.JSONDecodeError as e:
            print(f"❌ Error loading personal info: {e}")
            self.personal_data = self._default_personal_info()
    
    def _default_personal_info(self) -> Dict[str, Any]:
        """Default personal information"""
        return {
            "personal_info": {
                "name": "Jay Patel",
                "role": "AI Developer",
                "bio": "I'm Jay, an AI developer working on intelligent systems.",
                "expertise": ["Python", "AI/ML", "Web Development"],
                "current_projects": ["AI Blog System"]
            }
        }
    
    def get_personal_context(self, query: str = "") -> str:
        """Get relevant personal context based on query"""
        personal_info = self.personal_data.get("personal_info", {})
        
        # Check what type of personal information is being requested
        query_lower = query.lower()
        
        context = ""
        
        # About me queries
        if any(keyword in query_lower for keyword in ["who are you", "about you", "tell me about", "your name", "introduce"]):
            context = f"""
Personal Information:
Name: {personal_info.get('name', 'Jay Patel')}
Role: {personal_info.get('role', 'AI Developer')}
Bio: {personal_info.get('bio', 'AI Developer working on intelligent systems')}
"""
        
        # Skills and expertise queries
        elif any(keyword in query_lower for keyword in ["skills", "expertise", "experience", "what can you do", "technologies"]):
            expertise = personal_info.get('expertise', [])
            skills = personal_info.get('skills', {})
            
            context = f"""
Technical Expertise:
• Programming Languages: {', '.join(skills.get('programming', expertise[:4]))}
• AI/ML Technologies: {', '.join(skills.get('ai_ml', ['LangChain', 'ChromaDB']))}
• Frameworks: {', '.join(skills.get('frameworks', ['FastAPI', 'React']))}
• Specialties: {', '.join(expertise)}
"""
        
        # Current projects queries
        elif any(keyword in query_lower for keyword in ["projects", "working on", "current work", "building"]):
            projects = personal_info.get('current_projects', [])
            context = f"""
Current Projects:
{chr(10).join([f'• {project}' for project in projects])}
"""
        
        # Contact queries
        elif any(keyword in query_lower for keyword in ["contact", "reach", "connect", "email", "github"]):
            contact = personal_info.get('contact', {})
            context = f"""
Contact Information:
• GitHub: {contact.get('github', 'Not specified')}
• Email: {contact.get('email', 'Not specified')}
• LinkedIn: {contact.get('linkedin', 'Not specified')}
"""
        
        # Philosophy/approach queries
        elif any(keyword in query_lower for keyword in ["philosophy", "approach", "believe", "values"]):
            philosophy = personal_info.get('philosophy', 'Building intelligent systems that make information accessible.')
            context = f"""
My Philosophy & Approach:
{philosophy}
"""
        
        # Fun facts queries
        elif any(keyword in query_lower for keyword in ["fun fact", "interesting", "hobby", "personal"]):
            fun_facts = personal_info.get('fun_facts', [])
            context = f"""
Fun Facts About Me:
{chr(10).join([f'• {fact}' for fact in fun_facts])}
"""
        
        # General personal query - return comprehensive info
        elif any(keyword in query_lower for keyword in ["personal", "about", "who", "yourself"]):
            name = personal_info.get('name', 'Jay Patel')
            role = personal_info.get('role', 'AI Developer')
            bio = personal_info.get('bio', 'AI Developer')
            interests = personal_info.get('interests', [])
            
            context = f"""
About {name}:
Role: {role}
Background: {bio}

Interests: {', '.join(interests[:5])}

I'm passionate about building AI systems that solve real-world problems and make information more accessible to everyone.
"""
        
        return context.strip()
    
    def is_personal_query(self, query: str) -> bool:
        """Check if query is asking for personal information"""
        personal_keywords = [
            "who are you", "about you", "your name", "tell me about yourself",
            "your skills", "your expertise", "your experience", "your projects",
            "your contact", "your github", "your email", "your philosophy",
            "about jay", "jay patel", "who is jay", "introduce yourself",
            "your background", "your interests", "what do you do"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in personal_keywords)
    
    def get_comprehensive_info(self) -> Dict[str, Any]:
        """Get all personal information"""
        return self.personal_data.get("personal_info", {})
    
    def update_personal_info(self, updates: Dict[str, Any]) -> bool:
        """Update personal information"""
        try:
            personal_info = self.personal_data.get("personal_info", {})
            personal_info.update(updates)
            self.personal_data["personal_info"] = personal_info
            
            # Save to file
            with open(self.personal_info_path, 'w', encoding='utf-8') as f:
                json.dump(self.personal_data, f, indent=2, ensure_ascii=False)
            
            print("✅ Personal information updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error updating personal info: {e}")
            return False
    
    def get_context_for_ai_response(self, query: str) -> str:
        """Get context specifically formatted for AI responses"""
        if not self.is_personal_query(query):
            return ""
        
        context = self.get_personal_context(query)
        if context:
            return f"\n\n[Personal Context - Use this to answer personal questions about Jay:]:\n{context}\n"
        
        return ""
    
    def get_name(self) -> str:
        """Get the person's name"""
        return self.personal_data.get("personal_info", {}).get("name", "Jay Patel")
    
    def get_role(self) -> str:
        """Get the person's role"""
        return self.personal_data.get("personal_info", {}).get("role", "AI Developer")

# Global personal context manager
personal_context = PersonalContextManager()