"""Seed educational resources for the community page."""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.community_post import EducationalResource
import uuid
from datetime import datetime


def seed_resources(db: Session):
    """Seed educational resources with Alzheimer's content."""
    
    resources = [
        # Articles
        {
            "id": str(uuid.uuid4()),
            "title": "Understanding Alzheimer's Disease: A Comprehensive Guide",
            "description": "Learn about the causes, symptoms, and progression of Alzheimer's disease from leading medical experts.",
            "content": """Alzheimer's disease is a progressive neurological disorder that affects memory, thinking, and behavior. It is the most common cause of dementia, accounting for 60-80% of cases.

**What Causes Alzheimer's?**
While the exact cause is not fully understood, researchers believe it involves a combination of genetic, lifestyle, and environmental factors. The disease is characterized by the buildup of abnormal proteins in the brain, including beta-amyloid plaques and tau tangles.

**Early Warning Signs:**
- Memory loss that disrupts daily life
- Challenges in planning or solving problems
- Difficulty completing familiar tasks
- Confusion with time or place
- Trouble understanding visual images
- Problems with words in speaking or writing
- Misplacing things and losing the ability to retrace steps
- Decreased or poor judgment
- Withdrawal from work or social activities
- Changes in mood and personality

**Stages of Alzheimer's:**
1. **Preclinical Stage**: No symptoms but brain changes are occurring
2. **Mild Cognitive Impairment**: Noticeable memory problems but can still function independently
3. **Mild Alzheimer's**: Memory loss and cognitive difficulties become more apparent
4. **Moderate Alzheimer's**: Increased memory loss and confusion, may need help with daily activities
5. **Severe Alzheimer's**: Loss of ability to respond to environment, communicate, and control movement

**Risk Factors:**
- Age (65 and older)
- Family history and genetics (APOE-e4 gene)
- Head trauma
- Heart health conditions
- Education and cognitive engagement

**Prevention Strategies:**
- Regular physical exercise
- Heart-healthy diet (Mediterranean or MIND diet)
- Mental stimulation and lifelong learning
- Social engagement
- Quality sleep
- Stress management
- Cardiovascular health management""",
            "resource_type": "article",
            "author": "Dr. Sarah Johnson, Neurologist",
            "source_url": "https://www.alz.org/alzheimers-dementia/what-is-alzheimers",
            "tags": "alzheimers,basics,symptoms,prevention",
            "is_featured": True,
            "view_count": 1247
        },
        {
            "id": str(uuid.uuid4()),
            "title": "The MIND Diet: Eating for Brain Health",
            "description": "Discover how the MIND diet combines Mediterranean and DASH diets to support cognitive function and reduce Alzheimer's risk.",
            "content": """The MIND diet (Mediterranean-DASH Intervention for Neurodegenerative Delay) is specifically designed to promote brain health and reduce the risk of Alzheimer's disease.

**10 Brain-Healthy Food Groups:**
1. **Green Leafy Vegetables** (6+ servings/week)
   - Kale, spinach, collards, lettuce
   - Rich in folate, vitamin E, and antioxidants

2. **Other Vegetables** (1+ serving/day)
   - Variety of colorful vegetables
   - Provides essential nutrients and fiber

3. **Nuts** (5+ servings/week)
   - Almonds, walnuts, cashews
   - High in healthy fats and vitamin E

4. **Berries** (2+ servings/week)
   - Blueberries and strawberries specifically
   - Packed with antioxidants

5. **Beans** (3+ servings/week)
   - Lentils, chickpeas, black beans
   - Excellent protein and fiber source

6. **Whole Grains** (3+ servings/day)
   - Oatmeal, quinoa, brown rice
   - Provides sustained energy

7. **Fish** (1+ serving/week)
   - Salmon, tuna, mackerel
   - Rich in omega-3 fatty acids

8. **Poultry** (2+ servings/week)
   - Chicken, turkey
   - Lean protein source

9. **Olive Oil** (primary cooking oil)
   - Extra virgin olive oil
   - Heart and brain healthy fats

10. **Wine** (1 glass/day, optional)
    - Red wine in moderation
    - Contains resveratrol

**Foods to Limit:**
- Red meat (less than 4 servings/week)
- Butter and margarine (less than 1 tablespoon/day)
- Cheese (less than 1 serving/week)
- Pastries and sweets (less than 5 servings/week)
- Fried or fast food (less than 1 serving/week)

**Sample MIND Diet Day:**
- Breakfast: Oatmeal with blueberries and walnuts
- Lunch: Spinach salad with grilled chicken, olive oil dressing
- Snack: Handful of almonds
- Dinner: Baked salmon with quinoa and roasted vegetables
- Beverage: Green tea or water

**Research Results:**
Studies show that strict adherence to the MIND diet can reduce Alzheimer's risk by up to 53%, while even moderate adherence shows a 35% risk reduction.""",
            "resource_type": "article",
            "author": "Dr. Martha Clare Morris, Nutritional Epidemiologist",
            "source_url": "https://www.rush.edu/news/diet-may-help-prevent-alzheimers",
            "tags": "diet,nutrition,prevention,mind-diet",
            "is_featured": True,
            "view_count": 892
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Exercise and Brain Health: The Connection",
            "description": "Learn how physical activity protects your brain and may reduce Alzheimer's risk by up to 50%.",
            "content": """Regular physical exercise is one of the most powerful tools for maintaining brain health and reducing Alzheimer's risk.

**How Exercise Protects the Brain:**
- Increases blood flow to the brain
- Promotes growth of new brain cells (neurogenesis)
- Reduces inflammation
- Improves insulin sensitivity
- Enhances mood and reduces stress
- Strengthens connections between brain cells
- Increases brain volume in key areas

**Recommended Exercise Guidelines:**
- **Aerobic Exercise**: 150 minutes/week of moderate intensity
  - Brisk walking, swimming, cycling, dancing
  - Aim for 30 minutes, 5 days per week

- **Strength Training**: 2-3 sessions/week
  - Weight lifting, resistance bands, bodyweight exercises
  - Builds muscle and bone strength

- **Balance and Flexibility**: Daily practice
  - Yoga, tai chi, stretching
  - Reduces fall risk and improves mobility

**Best Exercises for Brain Health:**
1. **Walking**: Simple, accessible, highly effective
2. **Swimming**: Low-impact, full-body workout
3. **Dancing**: Combines physical and cognitive challenges
4. **Tai Chi**: Improves balance and mental focus
5. **Cycling**: Cardiovascular benefits
6. **Yoga**: Reduces stress, improves flexibility

**Getting Started:**
- Start slowly and gradually increase intensity
- Choose activities you enjoy
- Exercise with friends for social benefits
- Set realistic goals
- Track your progress
- Consult your doctor before starting new programs

**Research Evidence:**
- Regular exercisers have 50% lower risk of developing Alzheimer's
- Exercise can slow cognitive decline in those with MCI
- Physical activity improves memory and executive function
- Even light activity is better than none

**Tips for Success:**
- Schedule exercise like any important appointment
- Find an exercise buddy for accountability
- Mix different types of activities
- Listen to music or podcasts while exercising
- Celebrate small victories""",
            "resource_type": "article",
            "author": "Dr. John Ratey, Harvard Medical School",
            "source_url": "https://www.health.harvard.edu/mind-and-mood/exercise-can-boost-your-memory-and-thinking-skills",
            "tags": "exercise,prevention,physical-activity,brain-health",
            "is_featured": False,
            "view_count": 654
        },
        
        # Videos
        {
            "id": str(uuid.uuid4()),
            "title": "What Happens to the Brain in Alzheimer's Disease?",
            "description": "An animated explanation of the biological changes that occur in the brain during Alzheimer's disease.",
            "content": """This educational video provides a clear, visual explanation of what happens in the brain during Alzheimer's disease.

**Video Topics Covered:**
- Normal brain function and neuron communication
- Formation of beta-amyloid plaques
- Development of tau tangles
- Brain cell death and tissue loss
- Impact on memory and cognitive function
- Progression through different brain regions

**Key Takeaways:**
- Alzheimer's begins with microscopic changes years before symptoms appear
- Plaques and tangles disrupt normal brain cell communication
- The hippocampus (memory center) is affected first
- Disease gradually spreads to other brain regions
- Understanding the biology helps in developing treatments

**Duration**: 8 minutes
**Recommended for**: Patients, families, caregivers, students

**Watch on YouTube**: Search for "Alzheimer's Disease - What Happens to the Brain" by the Alzheimer's Association""",
            "resource_type": "video",
            "author": "Alzheimer's Association",
            "source_url": "https://www.youtube.com/watch?v=yJXTXN4xrI8",
            "tags": "video,education,brain,biology",
            "is_featured": True,
            "view_count": 2103
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Caregiver Self-Care: Preventing Burnout",
            "description": "Essential strategies for caregivers to maintain their own health while caring for someone with Alzheimer's.",
            "content": """This video addresses the critical importance of caregiver self-care and provides practical strategies to prevent burnout.

**Topics Covered:**
- Recognizing signs of caregiver stress and burnout
- Setting realistic expectations
- Asking for and accepting help
- Taking regular breaks (respite care)
- Maintaining your own health appointments
- Staying connected with friends and support groups
- Managing difficult emotions
- Finding moments of joy

**Signs of Caregiver Burnout:**
- Feeling overwhelmed or constantly worried
- Feeling tired often
- Getting too much or too little sleep
- Gaining or losing weight
- Becoming easily irritated or angry
- Losing interest in activities you used to enjoy
- Feeling sad or depressed
- Having frequent headaches or body pain

**Self-Care Strategies:**
1. **Physical Health**: Exercise, eat well, get enough sleep
2. **Emotional Health**: Join support groups, see a therapist
3. **Social Connections**: Maintain friendships, stay engaged
4. **Respite Care**: Take regular breaks from caregiving
5. **Set Boundaries**: Learn to say no to additional demands
6. **Ask for Help**: Delegate tasks to family and friends

**Duration**: 12 minutes
**Recommended for**: Caregivers, family members

**Resources Mentioned:**
- Alzheimer's Association 24/7 Helpline: 1-800-272-3900
- Local support groups and respite care services
- Online caregiver communities""",
            "resource_type": "video",
            "author": "Family Caregiver Alliance",
            "source_url": "https://www.caregiver.org/resource/caregiver-self-care/",
            "tags": "video,caregiving,self-care,burnout",
            "is_featured": False,
            "view_count": 876
        },
        
        # Q&A
        {
            "id": str(uuid.uuid4()),
            "title": "Common Questions About Alzheimer's Diagnosis",
            "description": "Answers to frequently asked questions about getting diagnosed with Alzheimer's disease.",
            "content": """**Q: What tests are used to diagnose Alzheimer's?**
A: Diagnosis typically involves:
- Medical history review
- Physical and neurological examination
- Cognitive and memory tests (MMSE, MoCA)
- Brain imaging (MRI, CT, PET scans)
- Blood tests to rule out other conditions
- Sometimes cerebrospinal fluid analysis

**Q: Can Alzheimer's be diagnosed with certainty?**
A: A definitive diagnosis can only be made through brain autopsy after death. However, doctors can diagnose "probable Alzheimer's" with about 90% accuracy using clinical assessments and tests.

**Q: At what age should I be concerned about memory problems?**
A: While Alzheimer's typically affects people 65 and older, early-onset Alzheimer's can occur in people in their 40s and 50s. Any persistent memory problems that interfere with daily life should be evaluated, regardless of age.

**Q: Is memory loss a normal part of aging?**
A: Some mild memory changes are normal with aging (like occasionally forgetting names or where you put your keys). However, memory loss that disrupts daily life is not normal and should be evaluated.

**Q: Should I get genetic testing for Alzheimer's?**
A: Genetic testing is available but not routinely recommended. The APOE-e4 gene increases risk but doesn't guarantee you'll develop Alzheimer's. Discuss with a genetic counselor if you have strong family history.

**Q: What should I do if I'm worried about my memory?**
A: Schedule an appointment with your doctor. Early evaluation is important because:
- Memory problems might be due to treatable conditions
- Early diagnosis allows for better planning
- You can access treatments and clinical trials sooner
- You can make important decisions while still able

**Q: Can Alzheimer's be prevented?**
A: While there's no guaranteed prevention, you can reduce your risk through:
- Regular exercise
- Heart-healthy diet
- Mental stimulation
- Social engagement
- Managing cardiovascular risk factors
- Quality sleep
- Stress management

**Q: What treatments are available?**
A: Current treatments include:
- Medications (cholinesterase inhibitors, memantine)
- Lifestyle interventions
- Cognitive training
- Support services
- Clinical trials for new therapies

**Q: How fast does Alzheimer's progress?**
A: Progression varies greatly between individuals. On average, people live 4-8 years after diagnosis, but some live up to 20 years. Early diagnosis and good care can help maintain quality of life longer.""",
            "resource_type": "qa",
            "author": "Dr. Michael Chen, Geriatric Psychiatrist",
            "source_url": "https://www.nia.nih.gov/health/alzheimers-disease-fact-sheet",
            "tags": "qa,diagnosis,faq,testing",
            "is_featured": True,
            "view_count": 1456
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Questions About Caregiving for Someone with Alzheimer's",
            "description": "Practical answers to common caregiving questions and challenges.",
            "content": """**Q: How do I talk to someone with Alzheimer's?**
A: Communication tips:
- Speak slowly and clearly
- Use simple words and short sentences
- Maintain eye contact
- Be patient and allow time for responses
- Avoid arguing or correcting
- Use gentle touch and body language
- Minimize distractions
- Focus on feelings rather than facts

**Q: How do I handle repetitive questions?**
A: Strategies:
- Answer calmly each time
- Look for underlying needs (anxiety, boredom)
- Redirect to an activity
- Use memory aids (notes, calendars)
- Stay patient - they're not doing it intentionally

**Q: What do I do when they don't recognize me?**
A: This is heartbreaking but common:
- Don't take it personally
- Avoid saying "Don't you remember me?"
- Go along with their reality
- Focus on the emotional connection
- Use photos and familiar objects
- Maintain a calm, reassuring presence

**Q: How do I manage difficult behaviors?**
A: Approach:
- Identify triggers (pain, hunger, overstimulation)
- Maintain routines
- Simplify the environment
- Redirect attention
- Stay calm and reassuring
- Consult doctor about medication if needed

**Q: When is it time for a care facility?**
A: Consider when:
- Safety becomes a major concern
- Medical needs exceed home care capabilities
- Caregiver health is suffering
- Quality of life is declining for both
- Financial resources allow
- Discuss with family and healthcare team

**Q: How do I maintain their dignity?**
A: Important practices:
- Involve them in decisions when possible
- Respect their privacy
- Encourage independence in tasks they can do
- Avoid talking about them as if they're not there
- Celebrate their remaining abilities
- Treat them as the adult they are

**Q: What legal and financial planning is needed?**
A: Essential documents:
- Durable power of attorney
- Healthcare proxy/advance directives
- Will and estate planning
- Long-term care insurance review
- Social Security and Medicare enrollment
- Consult elder law attorney early

**Q: Where can I find support?**
A: Resources:
- Alzheimer's Association (1-800-272-3900)
- Local support groups
- Adult day care programs
- Respite care services
- Online caregiver communities
- Counseling services""",
            "resource_type": "qa",
            "author": "Nancy Pearce, MSW, Alzheimer's Care Specialist",
            "source_url": "https://www.alz.org/help-support/caregiving",
            "tags": "qa,caregiving,communication,behavior",
            "is_featured": False,
            "view_count": 723
        },
        
        # Guides
        {
            "id": str(uuid.uuid4()),
            "title": "Complete Guide to Creating a Dementia-Friendly Home",
            "description": "Step-by-step instructions for modifying your home to be safer and more comfortable for someone with Alzheimer's.",
            "content": """Creating a safe, comfortable environment is crucial for people with Alzheimer's disease. This guide provides practical modifications for every room.

**General Principles:**
- Reduce clutter and simplify spaces
- Improve lighting throughout
- Remove tripping hazards
- Use contrasting colors for important items
- Label drawers and cabinets with pictures
- Minimize noise and distractions
- Create clear pathways

**LIVING AREAS:**

**Safety Modifications:**
- Remove or secure loose rugs
- Ensure furniture is stable and sturdy
- Cover or remove mirrors if they cause confusion
- Install nightlights
- Remove or lock up dangerous items
- Secure electrical cords

**Comfort Enhancements:**
- Arrange furniture for easy navigation
- Provide comfortable seating with good support
- Keep familiar objects visible
- Use simple, clear labels
- Maintain consistent furniture placement

**KITCHEN:**

**Safety First:**
- Install stove shut-off devices
- Remove or lock up sharp objects
- Store cleaning products securely
- Use automatic shut-off appliances
- Install cabinet locks if needed
- Remove or disable garbage disposal

**Helpful Modifications:**
- Label cabinets with pictures
- Keep frequently used items accessible
- Use unbreakable dishes
- Provide easy-to-use utensils
- Post simple instructions for appliances

**BATHROOM:**

**Critical Safety Features:**
- Install grab bars near toilet and in shower
- Use non-slip mats
- Remove locks on doors
- Set water heater to 120°F or lower
- Install raised toilet seat
- Use shower chair or bench

**Convenience Additions:**
- Label hot and cold faucets clearly
- Use nightlights
- Keep bathroom well-lit
- Remove unnecessary items
- Use contrasting colors for toilet seat

**BEDROOM:**

**Sleep Environment:**
- Use nightlights
- Keep pathway to bathroom clear
- Remove clutter
- Use bed rails if needed
- Keep room at comfortable temperature

**Organization:**
- Label drawers with pictures
- Lay out clothes in order of dressing
- Use simple closet organization
- Keep familiar items visible
- Remove unnecessary furniture

**OUTDOOR SPACES:**

**Safety Measures:**
- Secure gates and fences
- Remove poisonous plants
- Ensure good lighting
- Create clear, safe pathways
- Install motion-sensor lights
- Consider GPS tracking devices

**Enjoyment Features:**
- Create comfortable seating areas
- Plant sensory gardens
- Provide shade
- Make spaces easily accessible
- Include familiar elements

**TECHNOLOGY AIDS:**

**Helpful Devices:**
- Automatic medication dispensers
- GPS tracking devices
- Motion sensors
- Video monitoring systems
- Smart home assistants (with simple commands)
- Picture phones
- Digital photo frames with familiar faces

**ROOM-BY-ROOM CHECKLIST:**

✓ Remove tripping hazards
✓ Improve lighting
✓ Install safety devices
✓ Simplify and declutter
✓ Add labels and signs
✓ Secure dangerous items
✓ Create clear pathways
✓ Use contrasting colors
✓ Maintain familiar layout
✓ Add comfort features

**ONGOING MAINTENANCE:**

- Regularly assess safety needs
- Adapt as disease progresses
- Keep emergency numbers visible
- Maintain consistent routines
- Update modifications as needed

**RESOURCES:**

- Occupational therapist home assessment
- Local Alzheimer's Association chapter
- Home modification contractors
- Assistive technology specialists""",
            "resource_type": "guide",
            "author": "Home Safety Council & Alzheimer's Association",
            "source_url": "https://www.alz.org/help-support/caregiving/safety/home-safety",
            "tags": "guide,home-safety,modifications,caregiving",
            "is_featured": True,
            "view_count": 1089
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Guide to Clinical Trials: Should You Participate?",
            "description": "Everything you need to know about Alzheimer's clinical trials, including how to find and evaluate them.",
            "content": """Clinical trials are research studies that test new treatments, interventions, or diagnostic tools. Participating in a trial can provide access to cutting-edge treatments while contributing to Alzheimer's research.

**UNDERSTANDING CLINICAL TRIALS:**

**What Are Clinical Trials?**
Research studies that test:
- New medications
- Behavioral interventions
- Diagnostic tools
- Prevention strategies
- Lifestyle modifications

**Types of Trials:**
1. **Prevention Trials**: Test ways to prevent Alzheimer's in healthy people
2. **Treatment Trials**: Test new medications or therapies
3. **Diagnostic Trials**: Develop better ways to diagnose Alzheimer's
4. **Quality of Life Trials**: Improve comfort and quality of life

**Trial Phases:**
- **Phase 1**: Small group, test safety
- **Phase 2**: Larger group, test effectiveness and side effects
- **Phase 3**: Large group, compare to standard treatments
- **Phase 4**: Post-approval, long-term effects

**BENEFITS OF PARTICIPATION:**

**For Participants:**
- Access to new treatments before public availability
- Close monitoring by medical team
- Contribute to advancing research
- No cost for trial-related care
- May receive compensation for time/travel

**For Research:**
- Advance understanding of Alzheimer's
- Develop new treatments
- Improve diagnostic tools
- Help future generations

**RISKS AND CONSIDERATIONS:**

**Potential Risks:**
- Unknown side effects
- Treatment may not work
- Time commitment required
- Possible placebo assignment
- Additional tests and procedures

**Important Questions:**
- What is being tested?
- What are the potential risks and benefits?
- What is the time commitment?
- Will I receive a placebo?
- What happens after the trial ends?
- Who will monitor my health?
- What costs will I incur?

**ELIGIBILITY:**

**Common Requirements:**
- Specific age range
- Diagnosis status (healthy, MCI, or Alzheimer's)
- Cognitive test scores
- Medical history criteria
- Availability for visits
- Study partner/caregiver participation

**May Exclude:**
- Certain medical conditions
- Current medications
- Recent participation in other trials
- Inability to undergo required tests

**FINDING TRIALS:**

**Resources:**
1. **ClinicalTrials.gov**: Official U.S. database
2. **Alzheimer's Association TrialMatch**: Free matching service
3. **Research centers**: Academic medical centers
4. **Physician referrals**: Ask your doctor
5. **Advocacy organizations**: Disease-specific groups

**Search Tips:**
- Use specific keywords
- Filter by location
- Check eligibility criteria
- Read full study descriptions
- Contact study coordinators

**EVALUATION PROCESS:**

**Before Enrolling:**
1. **Research the Study**:
   - Read protocol carefully
   - Understand purpose and procedures
   - Review risks and benefits

2. **Ask Questions**:
   - Speak with study coordinator
   - Consult your doctor
   - Talk to current participants if possible

3. **Review Informed Consent**:
   - Read thoroughly
   - Ask about anything unclear
   - Take time to decide
   - Discuss with family

4. **Consider Logistics**:
   - Visit frequency and location
   - Time commitment
   - Transportation needs
   - Caregiver requirements

**DURING THE TRIAL:**

**Your Rights:**
- Withdraw at any time
- Ask questions anytime
- Receive information about results
- Have privacy protected
- Receive appropriate care

**Your Responsibilities:**
- Attend all scheduled visits
- Follow protocol requirements
- Report side effects promptly
- Take medications as directed
- Keep study partner informed

**AFTER THE TRIAL:**

**Follow-up:**
- Continued monitoring may be offered
- Access to treatment may continue
- Results will be shared
- Transition plan to standard care

**Questions to Ask:**
- What are my next treatment options?
- Can I continue the study drug?
- What did researchers learn?
- Are there other trials available?

**MAKING THE DECISION:**

**Consider:**
- Your health goals
- Risk tolerance
- Time availability
- Family support
- Alternative options

**Discuss With:**
- Your doctor
- Family members
- Study coordinator
- Other participants

**Resources:**
- Alzheimer's Association: 1-800-272-3900
- TrialMatch: www.alz.org/trialmatch
- ClinicalTrials.gov
- Local research centers

**Remember**: Participation is voluntary. You can withdraw at any time for any reason. Your decision should be based on careful consideration of your personal situation and goals.""",
            "resource_type": "guide",
            "author": "Dr. Rebecca Edelmayer, Alzheimer's Association",
            "source_url": "https://www.alz.org/alzheimers-dementia/research_progress/clinical-trials",
            "tags": "guide,clinical-trials,research,treatment",
            "is_featured": False,
            "view_count": 567
        }
    ]
    
    # Check if resources already exist
    existing_count = db.query(EducationalResource).count()
    if existing_count > 0:
        print(f"Resources already exist ({existing_count} found). Skipping seed.")
        return
    
    # Add all resources
    for resource_data in resources:
        resource = EducationalResource(**resource_data)
        db.add(resource)
    
    db.commit()
    print(f"Successfully seeded {len(resources)} educational resources!")


def main():
    """Main function to seed resources."""
    db = SessionLocal()
    try:
        seed_resources(db)
    except Exception as e:
        print(f"Error seeding resources: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
