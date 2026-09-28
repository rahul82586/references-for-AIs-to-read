/**
 * Errors shared across transports.
 *
 * BackendGapError marks "the UI supports this, the backend doesn't (yet)".
 * It renders as a distinct warning badge in the UI and the running list of
 * these errors IS the work order for the backend session — the frontend never
 * fakes data to cover a gap.
 */
export class BackendGapError extends Error {
    readonly kind = 'backend-gap' as const;
    constructor(
        readonly capability: string,
        detail?: string
    ) {
        super(
            `Backend gap: ${capability} is not exposed by the API yet.` +
                (detail ? ` ${detail}` : '')
        );
        this.name = 'BackendGapError';
    }
}

export class ApiRequestError extends Error {
    readonly kind = 'api-request' as const;
    constructor(
        message: string,
        readonly status?: number
    ) {
        super(message);
        this.name = 'ApiRequestError';
    }
}

export function isBackendGap(e: unknown): e is BackendGapError {
    return e instanceof Error && (e as BackendGapError).kind === 'backend-gap';
}
