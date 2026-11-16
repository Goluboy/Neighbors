# Known gaps

Snapshot of 2026-11-16. Verify against code before trusting an item: it may already be fixed.
Fixed an item — delete its line in the same commit. Found a new defect — add a line here, not in
`AGENTS.md`.

1. `app/api/v1/bookings.py` wires `BookingService(db)`. The constructor is keyword-only: `uow`,
   `bookings`, `items`, `wallets`, `notifications`, `event_bus`. Wire it through `app/api/deps.py`
   and the container.
2. `create_booking(user, ...)` passes a `User`; the service expects `renter_id: int`. Pass
   `user.id`.
3. Services call `repo.add(dict(...))`, while `BaseSqlRepo.add(entity)` puts an object into the
   session, so a dict fails. Pick one contract and apply it to every repository.
4. `app/api/error_handlers.py` is referenced from `app/core/exceptions.py` but does not exist, so
   `DomainError` surfaces as 500 instead of 4xx.
5. Chat WebSocket: `chat_websocket` lacks the `@router.websocket` decorator, so the route does not
   exist and startup stays green.
6. `app/services/auth_service.py` has no `uow` and no commit (TODO), so `User` and `Wallet` never
   persist.
7. Tests cover `/health` and route-group presence only. No logic is covered.
