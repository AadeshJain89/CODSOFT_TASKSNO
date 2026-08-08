from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, or_, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from database import get_db
from models import Contact, User
from schemas import ContactCreate, ContactListResponse, ContactResponse, ContactUpdate

router = APIRouter(prefix="/api/contacts", tags=["Contacts"])


async def check_duplicate_contact(
    db: AsyncSession,
    user_id: int,
    email: Optional[str] = None,
    phone_number: Optional[str] = None,
    exclude_contact_id: Optional[int] = None
):
    """
    Check if a contact with the same email or phone number already exists for the given user.
    Throws 409 Conflict if duplicate found.
    """
    if email and email.strip():
        stmt = select(Contact).where(
            Contact.user_id == user_id,
            Contact.email.ilike(email.strip())
        )
        if exclude_contact_id:
            stmt = stmt.where(Contact.id != exclude_contact_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A contact with email '{email}' already exists in your contact list."
            )

    if phone_number and phone_number.strip():
        stmt = select(Contact).where(
            Contact.user_id == user_id,
            Contact.phone_number == phone_number.strip()
        )
        if exclude_contact_id:
            stmt = stmt.where(Contact.id != exclude_contact_id)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A contact with phone number '{phone_number}' already exists in your contact list."
            )


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_in: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new contact entry for authenticated user.
    Prevents duplicate email or phone number for the user (409 Conflict).
    """
    await check_duplicate_contact(
        db,
        user_id=current_user.id,
        email=contact_in.email,
        phone_number=contact_in.phone_number
    )

    new_contact = Contact(
        first_name=contact_in.first_name,
        last_name=contact_in.last_name,
        email=contact_in.email,
        phone_number=contact_in.phone_number,
        address=contact_in.address,
        company=contact_in.company,
        user_id=current_user.id
    )

    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


@router.get("", response_model=ContactListResponse)
async def list_contacts(
    search: Optional[str] = Query(None, description="Search across first_name, last_name, email, phone_number, company"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    sort_by: Literal["first_name", "last_name", "company", "created_at"] = Query("first_name", description="Field to sort by"),
    sort_order: Literal["asc", "desc"] = Query("asc", description="Sort order: asc or desc"),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum items to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve user contacts with multi-field search, company filter, sorting, and pagination.
    """
    query = select(Contact).where(Contact.user_id == current_user.id)

    # Search filter (first_name, last_name, email, phone_number, company)
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Contact.first_name.ilike(term),
                Contact.last_name.ilike(term),
                Contact.email.ilike(term),
                Contact.phone_number.ilike(term),
                Contact.company.ilike(term)
            )
        )

    # Filter by company
    if company and company.strip():
        query = query.where(Contact.company.ilike(f"%{company.strip()}%"))

    # Count query for total pagination metadata
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    # Sorting
    sort_attr = getattr(Contact, sort_by)
    query = query.order_by(asc(sort_attr) if sort_order == "asc" else desc(sort_attr))

    # Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    contacts = result.scalars().all()

    return ContactListResponse(
        total=total,
        items=list(contacts),
        skip=skip,
        limit=limit
    )


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact_by_id(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve single contact details by ID (Owner only).
    """
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    if contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this contact"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse)
async def full_update_contact(
    contact_id: int,
    contact_in: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Full update of a contact record (Owner only).
    """
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    if contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this contact"
        )

    await check_duplicate_contact(
        db,
        user_id=current_user.id,
        email=contact_in.email,
        phone_number=contact_in.phone_number,
        exclude_contact_id=contact.id
    )

    contact.first_name = contact_in.first_name
    contact.last_name = contact_in.last_name
    contact.email = contact_in.email
    contact.phone_number = contact_in.phone_number
    contact.address = contact_in.address
    contact.company = contact_in.company

    await db.commit()
    await db.refresh(contact)
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse)
async def partial_update_contact(
    contact_id: int,
    contact_in: ContactUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Partial update of a contact record (Owner only).
    """
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    if contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this contact"
        )

    update_data = contact_in.model_dump(exclude_unset=True)

    new_email = update_data.get("email", contact.email) if "email" in update_data else None
    new_phone = update_data.get("phone_number", contact.phone_number) if "phone_number" in update_data else None

    await check_duplicate_contact(
        db,
        user_id=current_user.id,
        email=new_email,
        phone_number=new_phone,
        exclude_contact_id=contact.id
    )

    for field, value in update_data.items():
        setattr(contact, field, value)

    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a contact by ID (Owner only).
    """
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    if contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this contact"
        )

    await db.delete(contact)
    await db.commit()
    return None
