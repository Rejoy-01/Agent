#!/usr/bin/env python3
"""
Final Hybrid Memory Chatbot
A real-world chatbot that works with all memory systems and uses populated knowledge.
"""

import asyncio
import re
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

# Import LLM
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class ExtractedInfo:
    """Information extracted from conversation"""
    medical_conditions: List[str] = None
    allergies: List[str] = None
    medications: List[str] = None
    current_symptoms: List[str] = None
    pain_level: Optional[str] = None
    preferences: List[str] = None
    
    def __post_init__(self):
        for field_name, field_value in self.__dict__.items():
            if field_value is None:
                setattr(self, field_name, [])

class FinalHybridChatbot:
    def __init__(self):
        print("🤖 Initializing Final Hybrid Memory Chatbot...")
        self.llm = self._init_llm()
        self.patient_name = ""
        self.conversation_history = []
        self.has_name = False
        print("✅ Chatbot ready with full memory access!")
        
    def _init_llm(self):
        """Initialize Groq LLM"""
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env file!")
        
        return ChatGroq(
            model="llama-3.1-8b-instant",
            api_key=groq_api_key,
            temperature=0.7
        )

    def extract_patient_name(self, text: str) -> bool:
        """Extract patient name from text"""
        if self.has_name:
            return True

        patterns = [
            r"(?:my name is|i'm|i am|call me)\s+([A-Za-z\s]+?)(?:\s*$|,|\.|!)",
            r"^([A-Za-z\s]+?)(?:\s+here|$|,|\.|!)"
        ]

        for pattern in patterns:
            match = re.search(pattern, text.strip(), re.IGNORECASE)
            if match:
                name = match.group(1).strip().title()
                # Filter out common greetings and short names
                if (name.lower() not in ['hello', 'hi', 'hey', 'good', 'there'] and
                    len(name) > 2):
                    self.patient_name = name
                    self.has_name = True
                    # Only print once when name is first extracted
                    if not hasattr(self, '_name_printed'):
                        print(f"👤 Patient name: {self.patient_name}")
                        self._name_printed = True
                    return True
        return False

    def extract_information_with_llm(self, text: str) -> ExtractedInfo:
        """Use LLM to intelligently extract and categorize medical information"""
        info = ExtractedInfo()

        if not self.has_name:
            return info

        # Use LLM to analyze and categorize the text
        analysis_prompt = f"""
        Analyze this patient statement and extract medical information. Categorize each piece of information:

        Patient statement: "{text}"

        Extract and categorize information into these categories:

        MEDICAL CONDITIONS: Any diseases, disorders, or chronic conditions (diabetes, asthma, hypertension, arthritis, etc.)

        ALLERGIES: Any allergies, intolerances, or adverse reactions (food allergies, drug allergies, environmental allergies like dust, pollen, etc.)

        MEDICATIONS: Any medications, drugs, treatments, or supplements being taken

        CURRENT SYMPTOMS: Current health complaints, symptoms, or problems happening now (pain, headache, nausea, etc.)

        PAIN LEVEL: Any pain scale ratings (1-10 scale, mild/moderate/severe)

        PREFERENCES: Appointment preferences, communication preferences, lifestyle habits, exercise habits

        Respond in this exact format:
        MEDICAL CONDITIONS: [list items separated by semicolons, or "none"]
        ALLERGIES: [list items separated by semicolons, or "none"]
        MEDICATIONS: [list items separated by semicolons, or "none"]
        CURRENT SYMPTOMS: [list items separated by semicolons, or "none"]
        PAIN LEVEL: [rating or "none"]
        PREFERENCES: [list items separated by semicolons, or "none"]

        Examples:
        - "I have dust allergy" → ALLERGIES: dust
        - "I'm allergic to shellfish" → ALLERGIES: shellfish
        - "My back hurts" → CURRENT SYMPTOMS: back pain
        - "I take pills for my heart" → MEDICATIONS: heart medication
        - "I have diabetes" → MEDICAL CONDITIONS: diabetes
        """

        try:
            response = self.llm.invoke(analysis_prompt).content

            # Parse the LLM response
            lines = response.strip().split('\n')

            for line in lines:
                if ':' in line:
                    category, items = line.split(':', 1)
                    category = category.strip().upper()
                    items = items.strip()

                    if items.lower() != 'none' and items:
                        item_list = [item.strip() for item in items.split(';') if item.strip()]

                        if 'MEDICAL CONDITIONS' in category:
                            info.medical_conditions.extend(item_list)
                        elif 'ALLERGIES' in category:
                            info.allergies.extend(item_list)
                        elif 'MEDICATIONS' in category:
                            info.medications.extend(item_list)
                        elif 'CURRENT SYMPTOMS' in category:
                            info.current_symptoms.extend(item_list)
                        elif 'PAIN LEVEL' in category:
                            info.pain_level = items
                        elif 'PREFERENCES' in category:
                            info.preferences.extend(item_list)

            # Print what was extracted for debugging (reduced output)
            if any([info.medical_conditions, info.allergies, info.medications,
                   info.current_symptoms, info.pain_level, info.preferences]):
                extracted_items = []
                if info.medical_conditions:
                    extracted_items.append(f"conditions: {len(info.medical_conditions)}")
                if info.allergies:
                    extracted_items.append(f"allergies: {len(info.allergies)}")
                if info.medications:
                    extracted_items.append(f"medications: {len(info.medications)}")
                if info.current_symptoms:
                    extracted_items.append(f"symptoms: {len(info.current_symptoms)}")
                if info.pain_level:
                    extracted_items.append("pain level")
                if info.preferences:
                    extracted_items.append(f"preferences: {len(info.preferences)}")

                print(f"🤖 Extracted: {', '.join(extracted_items)}")

        except Exception as e:
            print(f"❌ Error in LLM extraction: {e}")
            # Fallback to basic keyword extraction
            return self.extract_information_basic(text)

        return info

    def extract_information_basic(self, text: str) -> ExtractedInfo:
        """Fallback basic keyword extraction"""
        info = ExtractedInfo()
        text_lower = text.lower()

        # Basic patterns as fallback
        if any(word in text_lower for word in ["allergy", "allergic", "can't eat", "react to"]):
            # Try to extract what they're allergic to
            for word in ["dust", "pollen", "shellfish", "nuts", "penicillin", "latex"]:
                if word in text_lower:
                    info.allergies.append(word)

        if any(word in text_lower for word in ["diabetes", "asthma", "hypertension", "arthritis"]):
            conditions = re.findall(r"(diabetes|hypertension|asthma|arthritis|depression|anxiety)", text_lower)
            info.medical_conditions.extend(conditions)

        # Pain level
        pain_match = re.search(r"(\d+)\s*(?:out of|/)\s*10", text_lower)
        if pain_match:
            info.pain_level = f"{pain_match.group(1)}/10"

        return info

    def get_episodic_memory_direct(self) -> str:
        """Get episodic memory directly from SQLite"""
        try:
            conn = sqlite3.connect('medical_memory.db')
            cursor = conn.cursor()

            cursor.execute("""
                SELECT date, symptoms, diagnosis, prescription
                FROM visits
                WHERE patient_id = ?
                ORDER BY rowid DESC
                LIMIT 5
            """, (self.patient_name,))

            visits = cursor.fetchall()
            conn.close()

            if visits:
                visit_summaries = []
                for date, symptoms, diagnosis, prescription in visits:
                    visit_summaries.append(f"• {date}: {symptoms} → {diagnosis} → {prescription}")
                return "\n".join(visit_summaries)
            else:
                return "No previous visits found"

        except Exception as e:
            return f"Error loading visit history: {e}"

    def get_behavioral_memory_direct(self) -> str:
        """Get behavioral memory directly from SQLite"""
        try:
            conn = sqlite3.connect('behavioral_memory.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT missed_appointments, prefers_teleconsult, habit_notes 
                FROM behavior 
                WHERE patient_id = ?
            """, (self.patient_name,))
            
            behavior = cursor.fetchone()
            conn.close()
            
            if behavior:
                missed, prefers, notes = behavior
                return f"Missed appointments: {missed}; Prefers teleconsult: {prefers}; Notes: {notes}"
            else:
                return "No behavioral patterns found"
                
        except Exception as e:
            return f"Error loading behavioral data: {e}"

    def get_medical_facts_direct(self) -> str:
        """Get medical facts directly from SQLite"""
        try:
            conn = sqlite3.connect('medical_facts.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT fact_type, fact_value FROM medical_facts 
                WHERE patient_name = ?
                ORDER BY created_at DESC
            """, (self.patient_name,))
            
            facts = cursor.fetchall()
            conn.close()
            
            if facts:
                fact_groups = {}
                for fact_type, fact_value in facts:
                    if fact_type not in fact_groups:
                        fact_groups[fact_type] = []
                    fact_groups[fact_type].append(fact_value)
                
                fact_strings = []
                for fact_type, values in fact_groups.items():
                    fact_strings.append(f"{fact_type}: {', '.join(values)}")
                
                return "; ".join(fact_strings)
            else:
                return "No medical facts found"
                
        except Exception as e:
            return f"Error loading medical facts: {e}"

    def store_new_visit(self, info: ExtractedInfo):
        """Store new visit in episodic memory"""
        if not self.patient_name or not (info.current_symptoms or info.pain_level):
            return
            
        try:
            conn = sqlite3.connect('medical_memory.db')
            cursor = conn.cursor()
            
            symptoms_text = "; ".join(info.current_symptoms) if info.current_symptoms else "General consultation"
            diagnosis = f"Pain level: {info.pain_level}" if info.pain_level else "Assessment ongoing"
            
            cursor.execute("""
                INSERT INTO visits (patient_id, date, symptoms, diagnosis, prescription)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.patient_name,
                datetime.now().strftime("%Y-%m-%d"),
                symptoms_text,
                diagnosis,
                "Treatment plan pending"
            ))
            
            conn.commit()
            conn.close()
            print(f"📅 Stored new visit: {symptoms_text}")
            
        except Exception as e:
            print(f"❌ Error storing visit: {e}")

    def store_medical_facts(self, info: ExtractedInfo):
        """Store medical facts"""
        if not self.patient_name:
            return

        try:
            conn = sqlite3.connect('medical_facts.db')
            cursor = conn.cursor()

            for condition in info.medical_conditions:
                cursor.execute("""
                    INSERT INTO medical_facts (patient_name, fact_type, fact_value)
                    VALUES (?, ?, ?)
                """, (self.patient_name, "condition", condition))
                print(f"🏥 Stored condition: {condition}")

            for allergy in info.allergies:
                cursor.execute("""
                    INSERT INTO medical_facts (patient_name, fact_type, fact_value)
                    VALUES (?, ?, ?)
                """, (self.patient_name, "allergy", allergy))
                print(f"🚨 Stored allergy: {allergy}")

            for medication in info.medications:
                cursor.execute("""
                    INSERT INTO medical_facts (patient_name, fact_type, fact_value)
                    VALUES (?, ?, ?)
                """, (self.patient_name, "medication", medication))
                print(f"💊 Stored medication: {medication}")

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"❌ Error storing medical facts: {e}")

    def store_behavioral_info(self, info: ExtractedInfo):
        """Store behavioral information"""
        if not self.patient_name or not info.preferences:
            return

        try:
            conn = sqlite3.connect('behavioral_memory.db')
            cursor = conn.cursor()

            # Combine all preferences into notes
            notes_text = "; ".join(info.preferences)

            # Insert or update behavioral data
            cursor.execute("""
                INSERT OR REPLACE INTO behavior (patient_id, missed_appointments, prefers_teleconsult, habit_notes)
                VALUES (?, ?, ?, ?)
            """, (self.patient_name, 0, "unknown", notes_text))

            conn.commit()
            conn.close()
            print(f"👤 Stored behavioral info: {notes_text}")

        except Exception as e:
            print(f"❌ Error storing behavioral info: {e}")

    def get_patient_context(self) -> str:
        """Get comprehensive patient context from all memory systems"""
        if not self.patient_name:
            return ""
        
        context_parts = [f"Patient: {self.patient_name}"]
        
        # Get medical facts
        medical_facts = self.get_medical_facts_direct()
        context_parts.append(f"Medical History: {medical_facts}")
        
        # Get visit history
        visit_history = self.get_episodic_memory_direct()
        context_parts.append(f"Recent Visits:\n{visit_history}")
        
        # Get behavioral patterns
        behavioral_info = self.get_behavioral_memory_direct()
        context_parts.append(f"Patient Preferences: {behavioral_info}")
        
        return "\n\n".join(context_parts)

    def generate_response(self, user_input: str) -> str:
        """Generate natural response with full context"""
        
        if not self.has_name:
            prompt = """
            You are a friendly medical assistant. The user just started talking to you.
            Greet them warmly and ask for their name in a natural way.
            Be professional but approachable.
            """
        else:
            context = self.get_patient_context()
            
            prompt = f"""
            You are a caring medical assistant talking to {self.patient_name}.
            
            PATIENT CONTEXT:
            {context}
            
            The patient just said: "{user_input}"
            
            Respond naturally and professionally:
            - If you recognize them from their medical history, acknowledge it warmly
            - If they mention symptoms, relate to their previous visits when relevant
            - If they mention new symptoms, ask appropriate follow-up questions
            - Reference their known conditions, allergies, and medications when relevant
            - Be empathetic and show continuity of care
            - Keep responses conversational and helpful
            
            Show that you know their medical history and care about their ongoing health.
            """
        
        try:
            response = self.llm.invoke(prompt).content
            return response
        except Exception as e:
            return f"I apologize, I'm having trouble right now. Could you please try again?"

    def process_message(self, user_input: str) -> str:
        """Main message processing with full memory integration"""
        
        # Extract name if we don't have it
        if not self.has_name:
            self.extract_patient_name(user_input)
        
        # Extract information using LLM intelligence
        extracted_info = self.extract_information_with_llm(user_input)
        
        # Store information in memory systems
        if self.has_name:
            self.store_new_visit(extracted_info)
            self.store_medical_facts(extracted_info)
            self.store_behavioral_info(extracted_info)
        
        # Generate response with full context
        response = self.generate_response(user_input)
        
        # Store conversation
        self.conversation_history.append({
            "user": user_input,
            "assistant": response,
            "timestamp": datetime.now().isoformat(),
            "extracted_info": extracted_info
        })
        
        return response

    def get_session_summary(self) -> Dict:
        """Get session summary"""
        return {
            "patient_name": self.patient_name,
            "has_name": self.has_name,
            "total_exchanges": len(self.conversation_history),
            "memory_systems_used": ["episodic", "behavioral", "medical_facts"]
        }

def main():
    """Main chat loop"""
    print("🩺 Final Hybrid Memory Medical Chatbot")
    print("=" * 45)
    print("Hello! I'm your medical assistant with access to your complete medical records.")
    print("Type 'quit' to end our conversation.\n")
    
    try:
        chatbot = FinalHybridChatbot()
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                print(f"\nAssistant: Thank you for chatting with me{', ' + chatbot.patient_name if chatbot.has_name else ''}! Take care!")
                
                summary = chatbot.get_session_summary()
                print(f"\n📊 Session Summary:")
                print(f"Patient: {summary['patient_name'] if summary['has_name'] else 'Name not provided'}")
                print(f"Total exchanges: {summary['total_exchanges']}")
                print(f"Memory systems used: {', '.join(summary['memory_systems_used'])}")
                break
            
            if not user_input:
                continue
            
            response = chatbot.process_message(user_input)
            print(f"\nAssistant: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nSorry, I encountered an error: {e}")
            print("Please try again.\n")

if __name__ == "__main__":
    main()
