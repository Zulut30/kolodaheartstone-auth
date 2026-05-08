from aiogram import Router

from app.handlers import admin, common, errors, payment, subscription

router = Router(name="app")
router.include_router(common.router)
router.include_router(subscription.router)
router.include_router(payment.router)
router.include_router(admin.router)
router.include_router(errors.router)
