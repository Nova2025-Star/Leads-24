import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.models.lead import Lead, LeadStatus
from app.models.quote import Quote, QuoteStatus, QuoteItem
from app.models.kpi import KPIEvent
from app.utils.kpi import log_event

def create_sample_data(db: Session):
    """Create sample data for development and testing"""
    # Check if data already exists
    if db.query(User).count() > 0:
        return
    
    print("Creating sample data...")
    
    # Create admin user
    admin = User(
        email="admin@t24leads.se",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # admin123
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(admin)
    
    # Create partner users
    partners = []
    regions = ["Stockholm", "Göteborg", "Malmö", "Uppsala", "Västerås"]
    
    for i in range(1, 6):
        region = regions[i-1] if i <= len(regions) else None
        partner = User(
            email=f"partner{i}@t24leads.se",
            hashed_password=f"$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # partner1
            full_name=f"Partner {i}",
            role=UserRole.PARTNER,
            region=region,
            is_active=True
        )
        db.add(partner)
        partners.append(partner)
    
    db.commit()
    
    # Create leads
    leads = []
    cities = {
        "Stockholm": ["Stockholm", "Solna", "Sundbyberg", "Nacka"],
        "Göteborg": ["Göteborg", "Mölndal", "Kungsbacka"],
        "Malmö": ["Malmö", "Lund", "Helsingborg"],
        "Uppsala": ["Uppsala", "Enköping"],
        "Västerås": ["Västerås", "Eskilstuna"]
    }
    
    tree_species = ["PINE", "SPRUCE", "OAK", "BEECH", "MAPLE", "ASH", "BIRCH"]
    operations = ["FELLING", "CROWN_REDUCTION", "MAINTENANCE_PRUNING", "DEAD_WOOD", "STUMP_GRINDING"]
    
    for i in range(1, 21):
        region = random.choice(regions)
        city = random.choice(cities[region])
        
        # Create lead with random data
        lead = Lead(
            customer_name=f"Customer {i}",
            customer_email=f"customer{i}@example.com",
            customer_phone=f"+46 70 123 45{i:02d}",
            region=region,
            city=city,
            postal_code=f"{random.randint(10, 99)}1 {random.randint(10, 99)}",
            address=f"Sample Street {i}",
            summary=f"Tree work needed in {city}",
            details=f"Customer needs work on {random.randint(1, 5)} trees. Species include {', '.join(random.sample(tree_species, 2))}.",
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            expires_at=datetime.utcnow() + timedelta(hours=48),
            status=LeadStatus.NEW
        )
        db.add(lead)
        leads.append(lead)
    
    db.commit()
    
    # Assign some leads to partners and create quotes
    for i, lead in enumerate(leads):
        if i < 15:  # Assign 15 out of 20 leads
            partner = partners[i % len(partners)]
            
            # Assign lead
            lead.assigned_partner_id = partner.id
            lead.status = LeadStatus.ASSIGNED
            lead.assigned_at = lead.created_at + timedelta(hours=random.randint(1, 12))
            
            # Log KPI event
            log_event(
                db=db,
                event_type="lead_assigned",
                lead_id=lead.id,
                user_id=partner.id,
                data=f"Lead assigned to partner {partner.full_name}"
            )
            
            # Some leads are accepted
            if i < 10:
                lead.status = LeadStatus.ACCEPTED
                lead.accepted_at = lead.assigned_at + timedelta(hours=random.randint(1, 24))
                
                # Log KPI event
                log_event(
                    db=db,
                    event_type="lead_accepted",
                    lead_id=lead.id,
                    user_id=partner.id,
                    data=f"Lead accepted by partner {partner.full_name}"
                )
                
                # Some leads have quotes
                if i < 7:
                    # Create quote
                    quote = Quote(
                        lead_id=lead.id,
                        status=QuoteStatus.DRAFT,
                        created_at=lead.accepted_at + timedelta(hours=random.randint(1, 48)),
                        total_amount=0,  # Will be calculated from items
                        commission_amount=0  # Will be calculated from items
                    )
                    db.add(quote)
                    db.flush()  # Get the quote ID
                    
                    # Create quote items
                    total_amount = 0
                    for j in range(random.randint(1, 3)):
                        cost = random.randint(1000, 5000)
                        total_amount += cost
                        
                        item = QuoteItem(
                            quote_id=quote.id,
                            quantity=random.randint(1, 3),
                            tree_species=random.choice(tree_species),
                            operation_type=random.choice(operations),
                            cost=cost
                        )
                        db.add(item)
                    
                    # Update quote totals
                    quote.total_amount = total_amount
                    quote.commission_amount = total_amount * 0.1  # 10% commission
                    
                    # Some quotes are sent
                    if i < 5:
                        quote.status = QuoteStatus.SENT
                        quote.sent_at = quote.created_at + timedelta(hours=random.randint(1, 24))
                        
                        lead.status = LeadStatus.QUOTED
                        lead.quoted_at = quote.sent_at
                        
                        # Log KPI event
                        log_event(
                            db=db,
                            event_type="quote_sent",
                            lead_id=lead.id,
                            quote_id=quote.id,
                            user_id=partner.id,
                            data=f"Quote sent to customer: {lead.customer_email}"
                        )
                        
                        # Some quotes are approved/declined
                        if i < 3:
                            quote.customer_response_at = quote.sent_at + timedelta(hours=random.randint(24, 72))
                            
                            if i < 2:  # Approved
                                quote.status = QuoteStatus.APPROVED
                                lead.status = LeadStatus.APPROVED
                                lead.customer_response_at = quote.customer_response_at
                                
                                # Log KPI event
                                log_event(
                                    db=db,
                                    event_type="quote_approved",
                                    lead_id=lead.id,
                                    quote_id=quote.id,
                                    data=f"Quote approved by customer"
                                )
                            else:  # Declined
                                quote.status = QuoteStatus.DECLINED
                                lead.status = LeadStatus.DECLINED
                                lead.customer_response_at = quote.customer_response_at
                                
                                # Log KPI event
                                log_event(
                                    db=db,
                                    event_type="quote_declined",
                                    lead_id=lead.id,
                                    quote_id=quote.id,
                                    data=f"Quote declined by customer"
                                )
    
    db.commit()
    print("Sample data created successfully!")
